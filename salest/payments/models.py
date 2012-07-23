from django.db import models
from salest.discounts.models import Discount
from salest.products.models import Product, ProductVariation
from paypal.standard.ipn.signals import payment_was_successful
import hashlib
from django.conf import settings

ORDER_STATUS = (
    ('Temp', 'Temp'),
    ('New', 'New'),
    ('Blocked', 'Blocked'),
    ('In Process', 'In Process'),
    ('Billed', 'Billed'),
    ('Shipped', 'Shipped'),
    ('Complete', 'Complete'),
    ('Cancelled', 'Cancelled'),
)

class Order(models.Model):
    """ Extended Order Class """
    cart = models.ForeignKey('cart.Cart')

    shipping_street1 = models.CharField(max_length=80, blank=True, null=True)
    shipping_street2 = models.CharField(max_length=80, blank=True, null=True)
    shipping_addressee = models.CharField(max_length=80, blank=True, null=True)
    shipping_state = models.CharField(max_length=50, blank=True, null=True)
    shipping_city = models.CharField(max_length=50, blank=True, null=True)
    shipping_postal_code = models.CharField(max_length=30,
                                                        blank=True, null=True)
    shipping_country = models.CharField(max_length=255, blank=True, null=True)

    billing_street1 = models.CharField(max_length=80, blank=True, null=True)
    billing_street2 = models.CharField(max_length=80, blank=True, null=True)
    billing_addressee = models.CharField(max_length=80, blank=True, null=True)
    billing_state = models.CharField(max_length=50, blank=True, null=True)
    billing_city = models.CharField(max_length=50, blank=True, null=True)
    billing_postal_code = models.CharField(max_length=30,
                                                        blank=True, null=True)
    billing_country = models.CharField(max_length=255, blank=True, null=True)
    items_price = models.DecimalField(max_digits=10, decimal_places=2,
                                                        blank=True, null=True)
    tax_price = models.DecimalField(max_digits=10, decimal_places=2,
                                         blank=True, null=True,
                                         default=0)
    card_number = models.IntegerField(max_length=4, blank=True, null=True)
    discount = models.ForeignKey(Discount, blank=True, null=True)
    status = models.CharField(choices=ORDER_STATUS, max_length=255)
    shipping_method = models.CharField(max_length=255, blank=True, null=True)
    shipping_price = models.DecimalField(max_digits=14,
                                     decimal_places=2,
                                     default='0')

    def get_total_quantity(self):
        """
        Return total quantity for this order
        """
        total_quantity = 0
        for order_item in self.orderitem_set.all():
            total_quantity = total_quantity + order_item.quantity
        return total_quantity

    def get_total_price(self):
        """
        Return full price of this order
        """
        total_price = 0
        for cart_item in self.orderitem_set.all():
            total_price = total_price + cart_item.get_total_price()
        return total_price

    def get_total_price_with_shiping(self):
        return self.get_total_price() + self.shipping_price

    def confirm(self):
        """
        Method for confirmation order
        """
        self.cart.set_no_active()
        self.status = "Billed"
        self.save()
        for item in self.orderitem_set.all():
            if hasattr(item.product, 'duration'):
                item.product.duration.confirm(self.cart.contact.user)

    @classmethod
    def generate_hash(cls, order_id, amount):
        textToHash = [str(order_id), str(amount), settings.SECRET_KEY]
        return hashlib.md5(''.join(textToHash)).hexdigest()


class OrderItem(models.Model):
    """ Extended OrderItem Class """
    order = models.ForeignKey(Order)
    date_creation = models.DateField(auto_now_add=True)
    product = models.ForeignKey(ProductVariation)
    unit_price = models.DecimalField(max_digits=14,
                                     decimal_places=2,
                                     blank=True,
                                     null=True)

    quantity = models.IntegerField()
    discount = models.DecimalField(max_digits=14, decimal_places=2, blank=True,
                                   null=True)

    def get_total_price(self):
        """ Method return full price for one product """
        total_price = self.unit_price * self.quantity
        return total_price

    def get_discont_price(self):
        """ Method return full price minus discount """
        total_price = self.get_total_price()
        discount_price = total_price - self.discoount
        return discount_price


SHIPPING_MODULES = (
                   ('DHL', 'DHL'),
                   ('USMail', 'USMail'),
                   ('NewPost', 'NewPost'),
                )

PAYMENT_MODULES = (
                   ('PayPal', 'PayPal'),
                   ('WebMoney', 'WebMoney'),
                   ('YandexMoney', 'YandexMoney'),
                )


class ShippingService(models.Model):
    """ Information about service delivery """
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=5,
                                decimal_places=2)
    time = models.TimeField()

    def get_service_for_user(self):
        return self.objects.all()


class State(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return "".join(self.name)


def paypall_success(sender, **kwargs):
    new_hash = Order.generate_hash(sender.item_number, sender.mc_gross)
    try:
        order = Order.objects.get(id=sender.item_number)
        old_hash = Order.generate_hash(order.id, order.get_total_price_with_shiping())
        if old_hash == new_hash:
            order.confirm()
        else:
            print 'error'
    except Order.DoesNotExist:
        pass

payment_was_successful.connect(paypall_success)