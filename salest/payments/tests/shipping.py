from django_webtest import WebTest
from mock import patch, Mock

from test_tools.utils import model_factory
from salest.cart.models import Cart
from salest.payments.shipping_processor import get_shipping_methods
from salest.payments.shipping_modules.flat.processor import\
    get_shipping_cost as flat_get_shipping_cost


class ShippingProcessorTestCase(WebTest):
    """
    Shipping processor test case
    """
    def test_get_shipping_methods(self):
        """
        Test that method return currect dict
        """
        cart = model_factory(Cart)
        expected_dict = {'flat': {'price': 20, 'name': 'Flat Shipping'}}
        settings = {'flat': 'salest.payments.shipping_modules.flat'}
        with patch('django.conf.settings.SHIPPING_MODULES', settings):
            current_dict = get_shipping_methods(cart)
            self.assertEqual(expected_dict, current_dict)


class FlatShippingModule(WebTest):
    """
    Flat Shipping module testcase
    """
    def test_get_shipping_cost(self):
        expected_value = 20
        cart = model_factory(Cart)
        current_value = flat_get_shipping_cost(cart)

        self.assertEqual(expected_value, current_value)
