"""
Test cases for forms
"""
import datetime

from mock import patch
from django_webtest import WebTest
from test_tools.utils import model_factory
from django.core.exceptions import ValidationError
from salest.payments.forms import PaymentForm, validate_card_number,\
    generate_year_list, generate_month_list, ChoiceShippingForm
from salest.payments.views import PrePaymentWizard
from django.test.client import RequestFactory
from salest.cart.models import Cart, CART_SESSION_KEY
from django.contrib.auth.models import User
from salest.payments.models import Order


class UtilsTestCase(WebTest):

    def test_validate_card_num_valid(self):
        """
        Test that form can validate credit card number
        """
        result = validate_card_number('4111111111111111')
        self.assertTrue(result)

    def test_validate_card_num_invalid(self):
        """
        Test that form can rise error when credit card number wrong
        """
        result = validate_card_number('41414141414141444')
        self.assertFalse(result)

    def test_generate_year_list(self):
        """ Test that generate_year_list returns right tuple """
        result = generate_year_list()
        now = datetime.datetime.now().year
        self.assertEqual(len(result), 10)
        self.assertEqual(result[-1], (now + 9, now + 9))

    def test_generate_month_list(self):
        """ Test that generate_month_list return right values """
        results = generate_month_list()
        self.assertEqual(results[-1], ('12', '12'))


class ChoiceShippingFormTestCase(WebTest):
    """
    Shipping form test case
    """

    def test_init(self):
        """
        Test that init work currect
        """
        choices = [(0, 0), (1, 2)]
        with patch('salest.payments.forms.SHIPPING_MODULES', choices):
            form = ChoiceShippingForm()
            self.assertEqual(form.fields['shipping_method'].choices, choices)

    def test_set_choices(self):
        """
        Test that method set variable currect
        """
        choices = [(1, 1), (2, 2)]
        ChoiceShippingForm().set_choices(choices)
        form = ChoiceShippingForm()
        self.assertEqual(form.fields['shipping_method'].choices, choices)

    def test_save(self):
        """
        Test that method set currect data to order
        """
        expected_list = ['flat', 20.0]

        cart = model_factory(Cart, save=True)
        order = model_factory(Order, cart=cart, save=True)
        request = RequestFactory()
        request.session = {'shipping_cost': 20}

        wizard = PrePaymentWizard()
        wizard.order = order
        wizard.request = request

        form = ChoiceShippingForm()
        form.cleaned_data = {'shipping_method': 'flat'}
        form.save(wizard)
        self.assertEqual(expected_list, [wizard.order.shipping_method,
                                         wizard.order.shipping_price])


class PaymentFormsTestCase(WebTest):
    """ Test payment forms """

    def test_validate_expire_date_valid(self):
        """
        Test that form can validate expire date
        """
        expire_month = datetime.datetime.now().month
        expire_year = datetime.datetime.now().year + 1
        form = PaymentForm()
        form.cleaned_data = {'expire_month': expire_month,
                            'expire_year': expire_year}
        result = form.validate_expire_date()
        self.assertTrue(result)

    def test_validate_expire_date_invalid(self):
        """
        Test that form rise exception when expire date is invalid
        """
        expire_month = datetime.datetime.now().month - 1
        expire_year = datetime.datetime.now().year
        form = PaymentForm()
        form.cleaned_data = {'expire_month': expire_month,
                            'expire_year': expire_year}
        result = form.validate_expire_date()
        self.assertFalse(result)

    def test_clean_method(self):
        """
        Test that clean method validates expire date
        """
        form = PaymentForm()
        form.cleaned_data = {}
        with patch('salest.payments.forms.PaymentForm.validate_expire_date')\
                                                                as valid_date:
            form.clean()
            valid_date.assert_called_once_with()

    def test_clean_card_number(self):
        """
        Test clean card number
        """
        expected_value = '4111111111111111'
        form = PaymentForm()
        form.cleaned_data = {'card_number': '4111-1111-1111-1111'}
        with patch('salest.payments.forms.validate_card_number') as valid_card:
            value = form.clean_card_number()
            valid_card.assert_called_once_with(expected_value)
        self.assertEqual(expected_value, value)

    def test_clean_ccv(self):
        """
        Test clean ccv code
        """
        expected_value = '123'
        form = PaymentForm()
        form.cleaned_data = {'ccv': expected_value}
        value = form.clean_ccv()
        self.assertEqual(expected_value, value)

    def test_clean_ccv_invalid(self):
        """
        Test clean ccv code
        """
        form = PaymentForm()
        form.cleaned_data = {'ccv': 'invalid cvv'}
        self.assertRaises(ValidationError, form.clean_ccv)
