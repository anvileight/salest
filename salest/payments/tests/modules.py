from contextlib import nested
from django_webtest import WebTest
from mock import patch, Mock

from test_tools.utils import model_factory
from paypal.standard.forms import PayPalPaymentsForm

from salest.payments.models import Order
from salest.cart.models import Cart
from django.test.client import RequestFactory
from salest.payments.views import PrePaymentWizard
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User
from salest.accounts.models import Contact

from salest.payments.payment_processor import (get_payment_forms, url_lookup,
                                                            get_confirm_view)
from salest.payments.modules.dummy.processor import\
                                        (DEFAULT_FORMS as dummy_default_forms)
from salest.payments.modules.dummy.urls import urlpatterns as dummy_urls
from salest.payments.modules.dummy.forms import DummyPaymentForm
from salest.payments.modules.trustcommerce.forms import\
                                                    TrustCommercePaymentForm
from salest.payments.modules.dummy.processor import\
                                    (ConfirmPaymentView as dummy_confirm_view,
                                     SucsessPaymentView as dummy_success_view)
from salest.payments.modules.trustcommerce.processor import\
    prepere_payment_information, get_error_message,\
    ConfirmPaymentView as trustcommerce_confirm,\
    SuccessPaymentView as trustcommerce_success, SuccessPaymentView
from salest.payments.modules.paypal.processor import\
                                    (ConfirmPaymentView as paypal_confirm,
                                     SucsessPaymentView as paypal_success)


PAYMENT_INFO_IN_SESSION = {'payment_data': {
                                          'credit_number': '4111111111111111',
                                          'ccv': '123',
                                          'expire': '1212'
                                          }
                           }

FORM_CLEANED_DATA = {'card_number': '4111111111111111', 'ccv': '123',
                                    'expire_month': '12', 'expire_year': '12'}


class PaymentManagerTestCase(WebTest):
    """
    Test Payment Manager
    """
    def test_get_payment_forms_method(self):
        """
        Test that method can return forms from module
        """
        with patch('django.conf.settings.PAYMENT_MODULES',
                                {'dummy': 'salest.payments.modules.dummy'}):
            forms_from_module = get_payment_forms('dummy')

            self.assertEquals(forms_from_module, dummy_default_forms)

    def test_get_payments_form_custom(self):
        """
        Test that method can return custom payment forms
        """
        custom_forms = [Mock()] * 3
        with patch('django.conf.settings.PAYMENT_MODULES',
                                {'dummy': 'salest.payments.modules.dummy'}):
            forms_from_module = get_payment_forms('dummy', custom_forms)
            self.assertEqual(custom_forms, forms_from_module)

    def test_url_lookup(self):
        """
        Test that method can find all urls from payment modules
        """
        with patch('django.conf.settings.PAYMENT_MODULES',
                                {'dummy': 'salest.payments.modules.dummy'}):
            urls = url_lookup()
            self.assertEqual(dummy_urls, urls)

    def test_get_confirm_view(self):
        """
        Test that method can return conformation view
        """
        request = RequestFactory().get('/')
        user = model_factory(User, username='test', save=True)
        cart = model_factory(Cart, contact=user.contact, is_active=True,
                                                                    save=True)
        request.user = user
        model_factory(Order, cart=cart, save=True)
        with patch('django.conf.settings.PAYMENT_MODULES',
                                {'dummy': 'salest.payments.modules.dummy'}):
            confirm_view = get_confirm_view('dummy')
            self.assertEqual(dummy_confirm_view, confirm_view)


class DummyModuleTestCase(WebTest):
    """
    Dummy module test case
    """
    def test_dummy_form_save_credit_number(self):
        """
        Test that dummy payment form save method save order
        """
        wizard = PrePaymentWizard()
        cart = model_factory(Cart, save=True)
        wizard.order = model_factory(Order, cart=cart)
        form = DummyPaymentForm()
        form.cleaned_data = FORM_CLEANED_DATA
        order = form.save(wizard)
        self.assertEqual(order.card_number, '1111')

    def test_dummy_confirm_view_context(self):
        """
        Test that method get_context_data return currect data
        """
        user = model_factory(User, save=True)
        cart = model_factory(Cart, is_active=True, contact=user.contact,
                                                                    save=True)
        order = model_factory(Order, cart=cart, save=True)
        request = RequestFactory().get('/')
        request.user = user
        request.cart = cart
        expected_dict = {'module_success_url': reverse('dummy_success'),
                         'order_id': order.id}
        current_dict = dummy_confirm_view(
                                        request=request).get_context_data()
        self.assertEqual(expected_dict, current_dict)

    def test_dummy_sucsess_get_context_data_confirm(self):
        """
        Test that method call order confirm method
        """
        cart = model_factory(Cart, is_active=True, save=True)
        order = model_factory(Order, cart=cart, save=True)
        request = RequestFactory().post('/', {'order_id': order.id})
        request.session = {}
        with patch('salest.payments.models.Order.confirm') as confirm:
            dummy_success_view(request=request).get_context_data()
            confirm.assert_called_once_with()

    def test_dummy_sucsess_remove_cart_from_session(self):
        """
        Test that success method call remove_cart_from_session
        """
        cart = model_factory(Cart, is_active=True, save=True)
        order = model_factory(Order, cart=cart, save=True)
        request = RequestFactory().post('/', {'order_id': order.id})
        request.session = {}
        with patch('salest.cart.models.CartManager.remove_cart_from_session')\
                                                                    as remove:
            dummy_success_view(request=request).get_context_data()
            remove.assert_called_once_with(request)

    def test_dummy_sucsess_get_context_data_context(self):
        """
        Test that method return currect context
        """
        user = model_factory(User, save=True)
        cart = model_factory(Cart, is_active=True, contact=user.contact,
                                                                    save=True)
        order = model_factory(Order, cart=cart, save=True)
        request = RequestFactory().get('/')
        request.user = user
        request = RequestFactory().post('/', {'order_id': order.id})
        request.session = {}
        expected_dict = {'order': order}
        current_dict = dummy_success_view(request=request).get_context_data()
        self.assertEqual(expected_dict, current_dict)


class TrustCommerceModuleTestCase(WebTest):
    """
    TrustCommerce payment method
    """

    def test_trustcommerce_confirm_view(self):
        """
        Test that view return currect data
        """
        user = model_factory(User, save=True)
        cart = model_factory(Cart, is_active=True, contact=user.contact,
                                                                    save=True)
        order = model_factory(Order, cart=cart, save=True)
        request = RequestFactory().get('/')
        request.user = user
        request.cart = cart
        expected_dict = {
                        'module_success_url': reverse('trustcommerce_success'),
                         'order_id': order.id}
        current_dict = trustcommerce_confirm(
                                        request=request).get_context_data()
        self.assertEqual(expected_dict, current_dict)

    def test_trustcommerce_sucsess_remove_cart_from_session(self):
        """
        Test that success method call remove_cart_from_session
        """
        cart = model_factory(Cart, is_active=True, save=True)
        order = model_factory(Order, cart=cart, save=True)
        request = RequestFactory().post('/', {'order_id': order.id})
        request.session = {}
        remove = Mock()
        pre_payment = Mock(return_value=({'status': 'appruved'}, order))
        with nested(patch('salest.cart.models.CartManager.remove_cart_from_session', remove),
                patch('salest.payments.modules.trustcommerce.processor.prepere_payment_information',
                                            pre_payment)):
            dummy_success_view(request=request).get_context_data()
            remove.assert_called_once_with(request)

    def test_trustcommerce_form_save_credit_number(self):
        """
        Test that method save last four number or credit cart
        """
        wizard = PrePaymentWizard()
        request = RequestFactory().get('/')
        request.session = {}
        wizard.request = request
        cart = model_factory(Cart, save=True)
        wizard.order = model_factory(Order, cart=cart)
        form = TrustCommercePaymentForm()
        form.cleaned_data = FORM_CLEANED_DATA
        order = form.save(wizard)
        self.assertEqual(order.card_number, '1111')

    def test_trustcommerce_form_save_session(self):
        """
        Test that method set data in session
        """
        expected_dict = PAYMENT_INFO_IN_SESSION.copy()
        wizard = PrePaymentWizard()
        request = RequestFactory().get('/')
        request.session = {}
        wizard.request = request
        cart = model_factory(Cart, save=True)
        wizard.order = model_factory(Order, cart=cart, save=True)
        form = TrustCommercePaymentForm()
        form.cleaned_data = FORM_CLEANED_DATA
        form.save(wizard)
        self.assertEqual(expected_dict, request.session)

    def test_get_error_message_method(self):
        """
        Test that method can return error_message
        """
        expect_value = 'Improperly formatted data. Offending fields: []'

        result = {'status': 'baddata', 'offenders': []}
        error_message = get_error_message(result)
        self.assertEqual(error_message, expect_value)

    def test_prepere_payment_information_result(self):
        """
        Test that method return transaction result
        """
        user = model_factory(User, first_name='test', last_name='test',
                                                                    save=True)
        cart = model_factory(Cart, contact=user.contact, is_active=True,
                                                                    save=True)
        order = model_factory(Order, cart=cart)
        payment_data = {'credit_number': '4111-1111-1111-1111',
                        'expire': '102012',
                        'ccv': 123}
        result = prepere_payment_information(order, payment_data)
        self.assertTrue(isinstance(result, dict))

    def test_tclink_call(self):
        """
        Test that tclink is called
        """
        user = model_factory(User, first_name='test', last_name='test',
                                                                    save=True)
        cart = model_factory(Cart, contact=user.contact, is_active=True,
                                                                    save=True)
        order = model_factory(Order, cart=cart, save=True)
        request = RequestFactory().post(path='/', data={'order_id': order.id})
        request.session = {'payment_data':
                                    {'credit_number': '4111-1111-1111-1111',
                                     'expire': '102012',
                                     'ccv': 123
                                     }
                           }
        view = SuccessPaymentView()
        view.request = request
        with patch('tclink.send') as tclinc:
            view.get_context_data()
            self.assertTrue(tclinc.call_count == 1)


class PayPalTestCase(WebTest):
    """
    PayPal payment module Test Case
    """
    def test_confirm_context(self):
        """
        Test that method return currect data
        """
        user = model_factory(User, save=True)
        cart = model_factory(Cart, is_active=True, contact=user.contact,
                                                                    save=True)
        order = model_factory(Order, cart=cart, save=True)
        request = RequestFactory().get('/')
        request.user = user
        request.cart = cart
        current_dict = paypal_confirm(request=request).get_context_data()
        self.assertTrue(isinstance(current_dict['form'], PayPalPaymentsForm))
        self.assertTrue(order == current_dict['order'])

#    def test_success_confirm(self):
#        """
#        Test that method call order confirm method
#        """
#        cart = model_factory(Cart, is_active=True, save=True)
#        order = model_factory(Order, cart=cart, save=True)
#        request = RequestFactory().post('/', {'order_id': order.id})
#        request.session = {}
#        with patch('salest.payments.models.Order.confirm') as confirm:
#            paypal_success(request=request).get_context_data()
#            confirm.assert_called_once_with()

#    def test_success_remove_cart_from_session(self):
#        """
#        Test that method remove cart from session
#        """
#        cart = model_factory(Cart, is_active=True, save=True)
#        order = model_factory(Order, cart=cart, save=True)
#        request = RequestFactory().post('/', {'order_id': order.id})
#        request.session = {}
#        with patch('salest.cart.models.CartManager.remove_cart_from_session')\
#                                                                    as remove:
#            paypal_success(request=request).get_context_data()
#            remove.assert_called_once_with(request)

#    def test_success_context(self):
#        """
#        Test that method return currect context
#        """
#        cart = model_factory(Cart, is_active=True, save=True)
#        order = model_factory(Order, cart=cart, save=True)
#        request = RequestFactory().post('/', {"order_id": order.id})
#        request.session = {}
#        expected_dict = {'order': order}
#        current_dict = paypal_success(request=request).get_context_data()
#        self.assertEqual(expected_dict, current_dict)
