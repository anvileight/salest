from django_webtest import WebTest
from salest.cart.interfaces import CartInterface
from mock import Mock



class CartInterfaceTestCase(WebTest):

    def test_get_items_price(self):
        cart_i = CartInterface()
        self.assertRaises(NotImplementedError, cart_i.get_items_price)

    def test_items_get(self):
        cart_i = CartInterface()
        self.assertRaises(NotImplementedError, lambda : cart_i.items)

    def test_items_get_set(self):
        cart_i = CartInterface()
        def dummy():
            cart_i.items = 'test'
        self.assertRaises(NotImplementedError, dummy)

    def test_add_product(self):
        cart_i = CartInterface()
        self.assertRaises(NotImplementedError, cart_i.add_product, Mock())
    
    def test_checkout(self):
        cart_i = CartInterface()
        self.assertRaises(NotImplementedError, cart_i.checkout)