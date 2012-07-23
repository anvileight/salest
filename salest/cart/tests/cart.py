"""
Test cases cart related functionality
"""
from django_webtest import WebTest
from salest.cart.models import Cart, CART_SESSION_KEY, CartItem, Order,\
    OrderItem
from django.test.client import RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from test_tools.utils import model_factory
from mock import patch, Mock
from salest.products.models import Product, ProductVariation
from salest.accounts.models import Contact, Address
from contextlib import nested
from salest.discounts.tests.validators import create_discounts
from salest.discounts.models import Discount


class ManagerTestCase(WebTest):
    """ Test cart manager methods """

    def test_create_anonymous_cart(self):
        """ Test that cart can be created for not logged in user """
        request = RequestFactory().get('/')
        request.session = {}
        request.user = AnonymousUser()
        expected_cart = model_factory(Cart, save=True)
        with patch('salest.cart.models.CartManager.create_active',
                   Mock(return_value=expected_cart)) as active:
            cart = Cart.objects.create_anonymous_cart(request)
            active.assert_called_once_with()
        self.assertTrue(CART_SESSION_KEY in request.session)
        self.assertEqual(cart.id, request.session[CART_SESSION_KEY])

    def test_get_anonymous_cart(self):
        """ Test that cart can be fetched for not logged in user """
        request = RequestFactory().get('/')
        expected_cart = model_factory(Cart, is_active=True, save=True)
        request.session = {
            CART_SESSION_KEY: expected_cart.id
        }
        request.user = AnonymousUser()
        actual_cart = Cart.objects.get_anonymous_cart(request)
        self.assertEqual(expected_cart, actual_cart)

    def test_get_wrong_anonymous_cart(self):
        """ Test that cart can be fetched for not logged in user """
        request = RequestFactory().get('/')
        request.session = {
            CART_SESSION_KEY: -1
        }
        request.user = AnonymousUser()
        actual_cart = Cart.objects.get_anonymous_cart(request)
        self.assertEqual(None, actual_cart)

    def test_create_with_request_user(self):
        """ Test that cart can be created from request and user logged in """
        request = RequestFactory().get('/')
        user = model_factory(User, save=True)
        request.user = user
        expected_cart = model_factory(Cart)
        with patch('salest.cart.models.CartManager.create_active',
                   Mock(return_value=expected_cart)) as active:
            Cart.objects.get_or_create_from_request(request)
            active.assert_called_once_with(contact=user.contact)

    def test_create_no_request_user(self):
        """ Test that cart can be created from request and user logged in """
        request = RequestFactory().get('/')
        request.session = {}
        request.user = AnonymousUser()
        with patch('salest.cart.models.CartManager.create_anonymous_cart') as \
                                                                    cart_meth:
            Cart.objects.get_or_create_from_request(request)
            cart_meth.assert_called_once_with(request)

    def test_get_existed_no_user(self):
        """ Test that cart can gets for anonymous user """
        request = RequestFactory().get('/')
        request.user = AnonymousUser()
        with patch('salest.cart.models.CartManager.get_anonymous_cart') as \
                                                                    cart_meth:
            Cart.objects.get_or_create_from_request(request)
            cart_meth.assert_called_once_with(request)

    def test_get_existed_user(self):
        """ Test that cart can gets for anonymous user """
        request = RequestFactory().get('/')
        user = model_factory(User, save=True)
        expected_cart = model_factory(Cart, contact=user.contact,
                                      is_active=True, save=True)
        request.user = user
        actual_cart = Cart.objects.get_or_create_from_request(request)
        self.assertEqual(expected_cart, actual_cart)

    def test_create_active_no_contact(self):
        """ Test that create_active creates active cart without contact """
        cart = Cart.objects.create_active()
        self.assertTrue(cart.is_active)

    def test_create_active_with_contact(self):
        """
        Test that create_active creates active cart with contact
        and update other carts to be inactive
        """
        contact = model_factory(Contact, save=True)
        old_cart = model_factory(Cart, contact=contact, is_active=True,
                                 save=True)
        new_cart = Cart.objects.create_active(contact=contact)
        self.assertTrue(new_cart.is_active)
        old_cart = Cart.objects.get(id=old_cart.id)
        self.assertFalse(old_cart.is_active)

    def test_remove_cart_from_session_method(self):
        """
        Test that method remove cart from session
        """
        request = RequestFactory().get('/')
        request.session = {CART_SESSION_KEY: 12}
        Cart.objects.remove_cart_from_session(request)
        self.assertFalse(CART_SESSION_KEY in request.session)


class CartTestCase(WebTest):
    """ Test cart methods """
    maxDiff = None

    def test_add_existing_product(self):
        """
        Test that cart item increase quantity if product already exists
        """
        cart = model_factory(Cart, save=True)
        product = model_factory(Product, save=True)
        product_variation = model_factory(ProductVariation, items_in_stock=1,
                                                    product=product, save=True)
        initial_quantity = 3
        expected_cart_item = model_factory(CartItem, product=product_variation,
                                           cart=cart,
                                           quantity=initial_quantity,
                                           save=True)
        cart.add_product(product_variation)
        actual_cart_item = cart.items.get()
        self.assertEqual(actual_cart_item.quantity, initial_quantity + 1)
        self.assertEqual(expected_cart_item, actual_cart_item)

    def test_add_new_product(self):
        """
        Test that cart item created if product not in cart yet
        """
        cart = model_factory(Cart, save=True)
        product = model_factory(Product, save=True)
        product_variation = model_factory(ProductVariation, items_in_stock=1,
                                                    product=product, save=True)
        cart.add_product(product_variation)
        actual_cart_item = cart.items.get()
        self.assertEqual(actual_cart_item.quantity, 1)
        self.assertEqual(actual_cart_item.product, product_variation)

    def test_add_out_of_stock_product(self):
        """
        Test that product can't be added if it out of stock
        """
        cart = model_factory(Cart, save=True)
        product = model_factory(Product, save=True)
        product_variation = model_factory(ProductVariation, items_in_stock=0,
                                                    product=product, save=True)
        self.assertRaises(AssertionError, cart.add_product, product_variation)

    def create_kw_by_order(self, order):
        kwargs = {}
        prefixes = ['shipping', 'billing']
        for field in Address().ADDRESS_FIELDS:
            for prefix in prefixes:
                value = order.__getattribute__('{0}_{1}'.format(prefix, field))
                get_field = lambda addr: {'{0}_{1}'.format(addr, field): value}
                kwargs.update(get_field(prefix))
        return kwargs

    def creaet_kw_by_address(self, address):
        kwargs = {}
        for field in address.ADDRESS_FIELDS:
            value = address.__getattribute__(field)
            get_field = lambda addr: {'{0}_{1}'.format(addr, field): value}

            if address.is_billing:
                kwargs.update(get_field('billing'))

            if address.is_billing:
                kwargs.update(get_field('shipping'))
        return kwargs

    def test_method_create_order(self):
        """
        Test that method create order
        """
        contact = model_factory(Contact, save=True)
        cart = model_factory(Cart, contact=contact, save=True)
        address = model_factory(Address, is_billing=True, is_shipping=True,
                                contact=contact, save=True)

        order = cart._create_order()
        kw_order = self.create_kw_by_order(order)
        kw_addres = self.creaet_kw_by_address(address)
        self.assertEqual(kw_order, kw_addres)

    def test_update_exist_order(self):
        """
        Test that method update exist order
        """
        contact = model_factory(Contact, save=True)
        cart = model_factory(Cart, contact=contact, save=True)

        address = model_factory(Address, is_billing=True, is_shipping=True,
                                contact=contact, save=True)

        model_factory(Order, cart=cart, save=True)
        order = cart._create_order()

        kw_order = self.create_kw_by_order(order)
        kw_addres = self.creaet_kw_by_address(address)
        self.assertEqual(kw_order, kw_addres)

    def test_create_order_diff_address(self):
        """
        Test that create order with different address
        """
        contact = model_factory(Contact, save=True)
        cart = model_factory(Cart, contact=contact, save=True)
        shipping = model_factory(Address, is_shipping=True,
                                                    contact=contact, save=True)
        billibg = model_factory(Address, is_billing=True,
                                                    contact=contact, save=True)
        order = cart._create_order()
        kw_order = self.create_kw_by_order(order)
        kw_addres = self.creaet_kw_by_address(shipping)
        kw_addres.update(self.creaet_kw_by_address(billibg))
        self.assertEqual(kw_order, kw_addres)

    def test_create_items(self):
        """
        Test that cart items add to order
        """
        contact = model_factory(Contact, save=True)
        product = model_factory(Product, save=True)
        product_variation = model_factory(ProductVariation, product=product,
                                                        num=3, save=True)
        cart = model_factory(Cart, contact=contact, save=True)
        model_factory(CartItem, cart=[cart] * 3, product=product_variation,
                                                                    save=True)
        order = model_factory(Order, cart=cart, save=True)

        cart._create_items(order)

        order_items = OrderItem.objects.filter(order=order)
        self.assertEqual(len(order_items), len(product_variation))
        actual_products = map(lambda item: item.product, order_items)
        self.assertEqual(actual_products, product_variation)

    def test_checkout(self):
        """
        Test checkout method
        """
        contact = model_factory(Contact, save=True)
        cart = model_factory(Cart, contact=contact, save=True)

        with nested(patch('salest.cart.models.Cart._create_order'),
                    patch('salest.cart.models.Cart._create_items'))\
                                            as(_create_order, _create_items):
            order = cart.checkout()
            self.assertGreater(_create_order.call_count, 0)
            _create_items.assert_called_once_with(order)

    def test_set_no_active_method(self):
        """
        Test that method set cart as no active
        """
        contact = model_factory(Contact, save=True)
        cart = model_factory(Cart, contact=contact, save=True)
        cart.set_no_active()
        self.assertFalse(cart.is_active)


    def test_get_items_price(self):
        cart = Cart.objects.create_active()
        product = model_factory(Product, save=True)
        product_variation = model_factory(ProductVariation, product=product,
                                          save=True)
        cart_item = model_factory(CartItem, cart=cart,
                                  product=product_variation, save=True)
        with patch('salest.cart.models.CartItem.get_cart_item_price',
                  Mock(return_value=10)):
            self.assertEqual(cart.get_items_price(), 10)

    def test_get_items_discount_price(self):
        cart = Cart.objects.create_active()
        product = model_factory(Product, save=True)
        product_variation = model_factory(ProductVariation, product=product,
                                          save=True)
        discount = model_factory(Discount, save=True)
        cart.discount.add(discount)
        cart_item = model_factory(CartItem, cart=cart,
                                  product=product_variation, save=True)
        with nested(patch('salest.cart.models.CartItem.get_cart_item_discount_price',
                    Mock(return_value=10),
                    patch('salest.discounts.models.Discount.process_discount',
                    Mock(return_value=10)))):
            self.assertEqual(cart.get_items_discount_price(), 10)

    def test_saved(self):
        cart = Cart.objects.create_active()
        with nested(patch('salest.cart.models.Cart.get_items_price',
                                 Mock(return_value=20)),
                    patch('salest.cart.models.Cart.get_items_discount_price',
                                 Mock(return_value=10))):
            self.assertEqual(cart.saved(), 10)

    def test_clear_cart(self):
        cart = Cart.objects.create_active()
        product = model_factory(Product, save=True)
        product_variation = model_factory(ProductVariation, product=product,
                                          save=True)
        discount = model_factory(Discount, save=True)
        cart.discount.add(discount)
        cart_item = model_factory(CartItem, cart=cart,
                                  product=product_variation, save=True)
        self.assertTrue(bool(cart.items.all()))
        cart.clear_cart()
        self.assertFalse(bool(cart.items.all()))

    def test_get_quantity(self):
        cart = Cart.objects.create_active()
        product = model_factory(Product, save=True)
        product_variation = model_factory(ProductVariation, product=product,
                                          save=True)
        discount = model_factory(Discount, save=True)
        cart.discount.add(discount)
        cart_item = model_factory(CartItem, cart=cart,
                                  product=product_variation,
                                  quantity=10,
                                  save=True)
        self.assertEqual(cart.get_quantity(), 10)

    def test_get_quantity_with_attr(self):
        cart = Cart.objects.create_active()
        cart.quantity = 100
        self.assertEqual(cart.get_quantity(), 100)

    def test_add_discount(self):
        cart = Cart.objects.create_active()
        cart.contact = model_factory(Contact, save=True)
        cart.save()
        product = model_factory(Product, save=True)
        product_variation = model_factory(ProductVariation, product=product,
                                          save=True)
        discount = model_factory(Discount, save=True)
        cart.add_discount(discount)
        used = discount.used.get(contact=cart.contact)
        self.assertEqual(used.already_used, 1)
        cart.add_discount(discount)
        used = discount.used.get(contact=cart.contact)
        self.assertEqual(used.already_used, 2)

    def test_get_items(self):
        cart = Cart.objects.create_active()
        product = model_factory(Product, save=True)
        product_variation = model_factory(ProductVariation, product=product,
                                          save=True)
        cart_item = model_factory(CartItem, cart=cart,
                                  product=product_variation,
                                  quantity=10,
                                  save=True)
        self.assertEqual(list(cart.get_items()), [cart_item])

    def test_unicode(self):
        cart = Cart.objects.create_active()
        self.assertEqual(str(cart), 'True')


class CartItemTestCase(WebTest):

    def test_get_cart_item_price(self):
        cart = Cart.objects.create_active()
        product = model_factory(Product, save=True)
        product_variation = model_factory(ProductVariation, product=product,
                                          save=True)
        cart_item = model_factory(CartItem, cart=cart,
                                  product=product_variation,
                                  quantity=10,
                                  save=True)
        with patch('salest.cart.models.CartItem.product_price',
                    Mock(return_value=10)):
            self.assertEqual(cart_item.get_cart_item_price(), 100)

    def test_get_cart_item_discount_price(self):
        cart = Cart.objects.create_active()
        product = model_factory(Product, save=True)
        product_variation = model_factory(ProductVariation, product=product,
                                          save=True)
        cart_item = model_factory(CartItem, cart=cart,
                                  product=product_variation,
                                  quantity=10,
                                  save=True)
        with patch('salest.cart.models.CartItem.discounted_price',
                    Mock(return_value=10)):
            self.assertEqual(cart_item.get_cart_item_discount_price(), 100)

    def test_product_price(self):
        cart = Cart.objects.create_active()
        product = model_factory(Product, save=True)
        product_variation = model_factory(ProductVariation, product=product,
                                          save=True)
        cart_item = model_factory(CartItem, cart=cart,
                                  product=product_variation,
                                  save=True)
        with patch('salest.products.models.ProductVariation.get_price',
                    Mock(return_value=10)):
            self.assertEqual(cart_item.product_price(), 10)


    def test_discounted_price(self):
        cart = Cart.objects.create_active()
        product = model_factory(Product, save=True)
        product_variation = model_factory(ProductVariation, product=product,
                                          save=True)
        cart_item = model_factory(CartItem, cart=cart,
                                  product=product_variation,
                                  save=True)
        discount = model_factory(Discount, save=True)
        cart_item.discount.add(discount)
        with patch('salest.discounts.models.Discount.process_discount',
                    Mock(return_value=10)):
            self.assertEqual(cart_item.discounted_price(), 10)

    def test_saved_ammount(self):
        cart = Cart.objects.create_active()
        product = model_factory(Product, save=True)
        product_variation = model_factory(ProductVariation, product=product,
                                          save=True)
        cart_item = model_factory(CartItem, cart=cart,
                                  product=product_variation,
                                  save=True)
        with nested( patch('salest.cart.models.CartItem.product_price',
                    Mock(return_value=20)),
                    patch('salest.cart.models.CartItem.discounted_price',
                    Mock(return_value=10))):
            self.assertEqual(cart_item.saved_ammount(), 10)