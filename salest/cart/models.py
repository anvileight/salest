"""
Provides common models for shop.
"""

from django.db import models
from django.db.models.aggregates import Count, Sum
from django.contrib.auth.models import AnonymousUser

from salest.products.models import Product, ProductVariation
from salest.discounts.models import Discount
from salest.core.signals import product_added_to_cart
from salest.payments.models import OrderItem, Order
from salest.cart.interfaces import CartInterface



DISCOUNT_SHIPPING_CHOICES = (
    ('NONE', 'None'),
    ('FREE', 'Free Shipping'),
    ('FREECHEAP', 'Cheapest shipping option is free'),
    ('APPLY', 'Apply the discount above to shipping')
)



CART_SESSION_KEY = 'cart_id'


class CartManager(models.Manager):
    """
    Cart manager provides additional functionality to manipulate with carts
    """

    def create_active(self, **kwargs):
        """
        Create an active cart and make other inactive for partiular contact
        """
        if 'contact' in kwargs:
            self.filter(contact=kwargs['contact'], is_active=True).update(
                                                            is_active=False)
        return self.create(is_active=True, **kwargs)

    def create_anonymous_cart(self, request):
        """ Create a cart for anonymous user """
        assert isinstance(request.user, AnonymousUser)
        cart = self.create_active()
        request.session[CART_SESSION_KEY] = cart.id
        return cart

    def get_anonymous_cart(self, request):
        """ Get cart from request for anonymous user """
        assert isinstance(request.user, AnonymousUser)
        if not CART_SESSION_KEY in request.session:
            return None
        try:
            return self.get(pk=request.session[CART_SESSION_KEY],
                            is_active=True)
        except Cart.DoesNotExist:
            del request.session[CART_SESSION_KEY]
            return None

#    def get_from_request(self, request):
#        """Check if cart exist return Cart else return None"""
#
#        user = request.user
#        if isinstance(user, AnonymousUser):
#            return self.get_anonymous_cart(request)
#        return user.contact.cart

    def get_or_create_from_request(self, request):
        """
        Check if user in request and creates either anonymous cart or
        regular one.
        """
        user = request.user
        if isinstance(user, AnonymousUser):
            return self.get_anonymous_cart(request) or \
                   self.create_anonymous_cart(request)
        try:
            return self.filter(contact__user=user, is_active=True
                           ).prefetch_related('items', 'items__discount',
                           ).get()
        except Cart.DoesNotExist:
            return self.create_active(contact=user.contact)

    def remove_cart_from_session(self, request):
        """
        Method for remove cart from session
        """
        if CART_SESSION_KEY in request.session:
            del request.session[CART_SESSION_KEY]


class Cart(models.Model, CartInterface):
    """ Extended Shoping Cart Class """
    contact = models.ForeignKey('accounts.Contact', null=True,
                                blank=True, related_name='carts')
    is_active = models.BooleanField()
    discount = models.ManyToManyField(Discount, null=True, blank=True)
    objects = CartManager()

    def get_items_price(self):
        items = self.items.all()
        return sum(map(lambda item: item.get_cart_item_price(), items))

    def get_items_discount_price(self):
        items = self.items.all()
        price = sum(map(lambda item: item.get_cart_item_discount_price(),
                       items))
        for discount in self.discount.all():
            price = discount.process_discount(price)
        return price

    def saved(self):
        return self.get_items_price() - self.get_items_discount_price()

    def add_product(self, product_variation, quantity=1):
        assert product_variation.items_in_stock
        try:
            cart_item = self.items.filter(product=product_variation).get()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(product=product_variation,
                                               cart=self,
                                               quantity=quantity)
        else:
            cart_item.quantity += quantity
            cart_item.save()
        product_added_to_cart.send(self, product=product_variation)
        return cart_item

    def checkout(self, **kwargs):
        defaults = {'items_price': self.get_items_discount_price()}
        order = self._create_order(**dict(defaults, **kwargs))
        self._create_items(order)
        return order

    def set_no_active(self):
        self.is_active = False
        self.save()

    def _create_items(self, order):
        """ Creates order items from cart items """
        order_items = []
        for cart_item in self.items.all():
            order_items.append(OrderItem(
                                    order=order,
                                    product=cart_item.product,
                                    quantity=cart_item.quantity,
                                    unit_price=cart_item.product.price))

        OrderItem.objects.bulk_create(order_items)

    def _create_order(self, **kwargs):
        """ Create new order and copy addressess to it from user's Contact """
        address_list = self.contact.address_set.all()
        for address in address_list:
            for field in address.ADDRESS_FIELDS:
                value = getattr(address, field)
                get_field = lambda addr: {'{0}_{1}'.format(addr, field): value}
                if address.is_billing:
                    kwargs.update(get_field('billing'))

                if address.is_billing:
                    kwargs.update(get_field('shipping'))

        order, created = Order.objects.get_or_create(cart=self,
                                                     defaults=kwargs)

        if not created:
            for field_name, field_value in kwargs.items():
                setattr(order, field_name, field_value)
            order.save()
            order.orderitem_set.all().delete()
        return order

    def clear_cart(self):
        self.items.all().delete()

    def get_quantity(self):
        if hasattr(self, 'quantity'):
            return self.quantity
        return self.items.all().aggregate(Sum('quantity'))['quantity__sum']

    def add_discount(self, discount):
        self.discount.add(discount)
        used, created = discount.used.get_or_create(contact=self.contact)
        if not created:
            used.already_used += 1
            used.save()

    def get_items(self):
        return self.items.all().prefetch_related('discount')

    def __unicode__(self):
        return '{0}'.format(self.is_active)


class CartItem(models.Model):
    """ Extended Shoping CartItem Class """
    cart = models.ForeignKey(Cart, related_name='items')
    quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(ProductVariation)
    discount = models.ManyToManyField(Discount, null=True, blank=True)

    def get_cart_item_price(self):
        """ Full price for every products in cart item """
        return self.product_price() * self.quantity

    def get_cart_item_discount_price(self):
        """ Full price for every products in cart item """
        return self.discounted_price() * self.quantity

    def product_price(self):
        """ Return product price """
        return self.product.get_price()

    def discounted_price(self):
        price = self.product_price()
        for discount in self.discount.all():
            price = discount.process_discount(price)
        return price

    def saved_ammount(self):
        return self.product_price() - self.discounted_price()
