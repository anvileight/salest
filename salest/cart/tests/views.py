from django_webtest import WebTest
from mock import Mock, patch
from test_tools.utils import model_factory
from django.core.urlresolvers import reverse
from salest.products.models import Product, ProductVariation
from django.test.client import RequestFactory
from salest.cart.views import CartItemAddView, CartDetailView
from salest.cart.models import Cart
from django.contrib.auth.models import User
from django.http import Http404
from salest.discounts.forms import CartCodeDiscount


class CartItemAddViewTestCase(WebTest):

    def test_get_404(self):
        product = model_factory(Product, save=True)
        product_variation = model_factory(ProductVariation, product=product,
                                          save=True)
        cart = Cart.objects.create_active()
        user = model_factory(User, save=True)
        request = RequestFactory().get('/')
        request.user = user
        request.cart = cart
        view = CartItemAddView()
        self.assertRaises(Http404, view.get, request, 0)

    def test_get(self):
        cart = Cart.objects.create_active()
        product = model_factory(Product, save=True)
        product_variation = model_factory(ProductVariation, product=product,
                                          save=True)
        user = model_factory(User, save=True)
        request = RequestFactory().get('/')
        request.user = user
        request.cart = cart
        view = CartItemAddView()
        with patch('salest.cart.models.Cart.add_product', Mock()) as test_cart:
            view.get(request, product_variation.id)
            test_cart.assert_called_once_with(product_variation)


class CartDetailViewTestCase(WebTest):
    def test_get_context_data(self):
        response = self.app.get(reverse('cart:detail'))
        self.assertTrue('cart_discount_form' in response.context)
        self.assertTrue(isinstance(response.context['cart_discount_form'],
                                   CartCodeDiscount))
