from django_webtest import WebTest
from salest.payments.models import Order, OrderItem
from test_tools.utils import model_factory
from salest.cart.models import Cart
from salest.products.models import Product, ProductVariation


class PaymentsModelTestCase(WebTest):
    """
    Test Case for Payments models
    """

    def test_order_get_total_quantity_method(self):
        """
        Test that method return currect value
        """
        cart = model_factory(Cart, save=True)
        order = model_factory(Order, cart=cart, save=True)
        product = model_factory(Product, save=True)
        product_variation = model_factory(ProductVariation, product=product,
                                                                    save=True)
        model_factory(OrderItem, order=order, product=product_variation,
                                                        quantity=10, save=True)
        model_factory(OrderItem, order=order, product=product_variation,
                                                        quantity=2, save=True)
        expected_value = 12
        current_value = order.get_total_quantity()
        self.assertEqual(expected_value, current_value)

    def test_order_get_total_price_method(self):
        """
        Test that method return currect value
        """
        cart = model_factory(Cart, save=True)
        order = model_factory(Order, cart=cart, save=True)
        product = model_factory(Product, save=True)
        product_variation = model_factory(ProductVariation, product=product,
                                                                    save=True)
        model_factory(OrderItem, order=order, product=product_variation,
                                        quantity=10, unit_price=200, save=True)
        model_factory(OrderItem, order=order, product=product_variation,
                                        quantity=2, unit_price=100, save=True)
        expected_value = 2200
        current_value = order.get_total_price()
        self.assertEqual(expected_value, current_value)

    def test_order_comfirm_method_cart(self):
        """
        Test that method set cart as no active
        """
        cart = model_factory(Cart, is_active=True, save=True)
        order = model_factory(Order, cart=cart, save=True)
        order.confirm()
        self.assertFalse(cart.is_active)

    def test_order_confirm_order_status(self):
        """
        Test that method change order status
        """
        cart = model_factory(Cart, is_active=True, save=True)
        order = model_factory(Order, cart=cart, save=True)
        order.confirm()
        self.assertEqual(order.status, 'Billed')

    def test_order_item_get_total_price_method(self):
        """
        Test that method return currect value
        """
        order_item = model_factory(OrderItem, quantity=5, unit_price=200)
        expected_value = 1000
        current_value = order_item.get_total_price()
        self.assertEqual(expected_value, current_value)
