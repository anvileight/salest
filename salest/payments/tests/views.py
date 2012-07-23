from django_webtest import WebTest
from salest.payments.views import PrePaymentWizard
from django.test.client import RequestFactory
from test_tools.utils import model_factory
from mock import Mock, patch
from django.contrib.auth.models import User
from salest.cart.models import Cart
from salest.payments.models import Order
from salest.payments.modules.dummy.forms import DummyPaymentForm
from contextlib import nested

@patch('salest.payments.views.PrePaymentWizard.process_custom_step', Mock())
class PaymentViewsTestCase(WebTest):

    def test_wizard_cart_checkout(self):
        """
        Test that wizard methot done call cart checkout method
        """
        request = RequestFactory().get('/')
        user = model_factory(User, save=True)
        cart = model_factory(Cart, contact=user.contact, is_active=True,
                                                                    save=True)
        model_factory(Order, cart=cart, save=True)

        request.user = user
        request.cart = cart
        wizard = PrePaymentWizard()
        wizard.request = request
        with patch('salest.cart.models.Cart.checkout') as cart_checkout:
            wizard.done([Mock(data={'payment_method': 'dummy'}),
                         Mock(data=[])])
            cart_checkout.assert_called_once_with()

    def test_wizard_form_save(self):
        """
        Test that wizard mwthod done save forms
        """
        request = RequestFactory().get('/')
        user = model_factory(User, save=True)
        cart = model_factory(Cart, contact=user.contact, is_active=True,
                                                                    save=True)
        model_factory(Order, cart=cart, save=True)

        request.user = user
        request.cart = cart
        wizard = PrePaymentWizard()
        wizard.request = request
        form1 = Mock(data={'payment_method': 'dummy'})
        form2 = Mock(data=[])
        wizard.done([form1, form2])
        self.assertTrue(form1.save.call_count == 1)
        self.assertTrue(form2.save.call_count == 1)

    def test_wizard_get_payment_method_from_data_method(self):
        """
        Test that method can return module name from forms data
        """
        form_list = [Mock(data={'payment_method': 'dummy'}), Mock(data=[])]
        wizard = PrePaymentWizard()
        expected_value = 'dummy'
        module_name = wizard.get_payment_method_from_data(form_list)
        self.assertEqual(expected_value, module_name)

    def test_wizard_get_payment_method_name_from_request_method(self):
        """
        Test that method can return module name from request
        """
        request = RequestFactory().post('/', {'payment_method': 'dummy'})
        wizard = PrePaymentWizard()
        wizard.request = request
        expected_value = 'dummy'
        module_name = wizard.get_payment_method_name_from_request()
        self.assertEqual(expected_value, module_name)

    def test_wizard_add_paymet_form_method(self):
        """
        Test that method add payment form to wizard from payment module
        """
        request = RequestFactory().post('/', {'payment_method': 'dummy'})
        request.session = {}
        form_with_method_name = Mock(data={'payment_method': 'dummy'})
        form_list = {'1': Mock(data=[]), '0': form_with_method_name}
        wizard = PrePaymentWizard()
        wizard.request = request
        wizard.steps = Mock(count=2)
        wizard.form_list = form_list
        with patch('django.conf.settings.PAYMENT_MODULES',
                                {'dummy': 'salest.payments.modules.dummy'}):
            wizard.add_paymet_form()
            self.assertIn(DummyPaymentForm, wizard.form_list.values())

    def test_remove_payment_form_if_change(self):
        """
        Test that method remove payment form from wizard if payment method
        change
        """
        last_form = Mock()
        form_list = {'0': Mock(), '1': Mock(), '2': last_form}
        request = RequestFactory().post('/', {'payment_method': 'paypal'})
        request.session = {'module_name': 'dummy'}
        wizard = PrePaymentWizard()
        wizard.form_list = form_list
        wizard.request = request
        wizard.remove_payment_form_if_change()
        self.assertFalse(last_form in wizard.form_list)

#    def test_call_remove_payment_form_if_change(self):
#        """
#        Test that remove_payment_form_if_change call in process_step
#        """
#        request = RequestFactory().post('/', {'shipping_method': 'flat'})
#        request.session = {'choice_data':
#                {'flat': {'price': 20, 'name': 'Flat Shipping'}}
#                          }
#        wizard = PrePaymentWizard()
#        wizard.request = request
#        with patch('salest.payments.views.PrePaymentWizard.remove_payment_form_if_change')\
#                                                                    as remove:
#            wizard.process_step(Mock())
#            remove.assert_called_once_with()

    def test_generate_choices(self):
        """
        Test that method generate currect choices
        """
        expected_list = [('flat', 'Flat Shipping ($20)')]
        wizard = PrePaymentWizard()
        choice_data = {'flat': {'price': 20, 'name': 'Flat Shipping'}}
        current_list = wizard.generate_choices(choice_data)
        self.assertEqual(expected_list, current_list)

    def test_store_shipping_cost(self):
        """
        Test that method store shipping cost
        """
        expected_value = 20
        request = RequestFactory().post('/', {'shipping_method': 'flat'})
        request.session = {'choice_data':
                {'flat': {'price': expected_value, 'name': 'Flat Shipping'}}
                          }
        wizard = PrePaymentWizard()
        wizard.request = request
        with patch('django.conf.settings.PAYMENT_MODULES',
                                {'dummy': 'salest.payments.modules.dummy'}):
            wizard.store_shipping_cost()
            self.assertEqual(expected_value, request.session['shipping_cost'])

#    def test_process_step_call_payment(self):
#        request = RequestFactory().post('/', {'shipping_method': 'flat'})
#        request.session = {'choice_data':
#                {'flat': {'price': 20, 'name': 'Flat Shipping'}}
#                          }
#        wizard = PrePaymentWizard()
#        wizard.request = request
#
#        with nested(patch(
#                  'salest.payments.views.PrePaymentWizard.add_paymet_form'),
#                patch(
#                'salest.payments.views.PrePaymentWizard.process_custom_step')
#                    ) as (add_paymet_form, step):
#            wizard.process_step(Mock())
#            add_paymet_form.assert_called_once_with()

    def test_process_step_call_shipping(self):
        request = RequestFactory().post('/', {'shipping_method': 'flat'})
        request.session = {'choice_data':
                {'flat': {'price': 20, 'name': 'Flat Shipping'}}
                          }
        wizard = PrePaymentWizard()
        wizard.request = request
        with patch(
                'salest.payments.views.PrePaymentWizard.store_shipping_cost') \
                    as store_shipping_cost:
            wizard.process_step(Mock())
            store_shipping_cost.assert_called_once_with()
