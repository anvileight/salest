"""
    Forms test case
"""

from contextlib import nested

from django_webtest import WebTest
from test_tools.utils import model_factory, get_fake_email
from mock import patch, Mock

from salest.accounts.models import Address, Contact, UserConfirmation
from salest.accounts.forms import SignupForm
from salest.accounts.forms import ShippingAddressForm, BillingAddressForm,\
    BaseAddressForm
from django.contrib.auth.models import User
from salest.payments.views import PrePaymentWizard


class AddressFormsTestCase(WebTest):
    """ Address forms test cases """

    def test_base_address_build(self):
        """
        Test that commit inherited fine
        """
        address = model_factory(Address)
        form = BaseAddressForm()
        with patch('django.forms.ModelForm.save', Mock(return_value=address)):
            address = form.save(commit=False)
        self.assertTrue(address.pk is None)

    def test_base_address_save(self):
        """
        Test that form save address with shipping=True and address is saved
        """
        wizard = PrePaymentWizard()
        wizard.contact = model_factory(Contact, save=True)
        address = model_factory(Address)
        form = BaseAddressForm()
        with patch('django.forms.ModelForm.save', Mock(return_value=address)):
            address = form.save(wizard=wizard)
        self.assertTrue(address.pk is not None)
        self.assertEqual(address.contact, wizard.contact)

    def test_shipping_address_save(self):
        """ Test that form save address with shipping=True"""
        address = model_factory(Address)
        form = ShippingAddressForm()
        base_save = Mock(return_value=address)
        commit_save = Mock(return_value=address)
        wizard = PrePaymentWizard()
        wizard.contact = model_factory(Contact, save=True)
        with nested(patch(
                    'salest.accounts.forms.BaseAddressForm.save', base_save),
                    patch('salest.accounts.forms.InstanceSaveCommitMixin.save',
                          commit_save)):
            address = form.save(wizard=wizard)

        base_save.assert_called_once_with(form, commit=False, wizard=wizard)

        commit_save.assert_called_once_with(form, commit=True)
        self.assertTrue(address.is_shipping)

    def test_billing_address_save(self):
        """ Test that form save address with shipping=True"""
        address = model_factory(Address)
        form = BillingAddressForm()
        base_save = Mock(return_value=address)
        commit_save = Mock(return_value=address)
        wizard = PrePaymentWizard()
        wizard.contact = model_factory(Contact, save=True)
        with nested(patch(
                    'salest.accounts.forms.BaseAddressForm.save', base_save),
                    patch('salest.accounts.forms.InstanceSaveCommitMixin.save',
                          commit_save)):
            address = form.save(wizard=wizard)
        base_save.assert_called_once_with(form, commit=False, wizard=wizard)
        commit_save.assert_called_once_with(form, commit=True)
        self.assertTrue(address.is_billing)


class SignupTestCase(WebTest):
    """ Test signup form """

    def test_email_send(self):
        user = model_factory(User, email=get_fake_email(), save=True)
        form = SignupForm()
        form.instance = user
        email_meth = Mock()
        with patch('salest.core.models.EmailTemplate.send', email_meth):
            form.send_email()
            self.assertEqual(email_meth.call_count, 1)
            confirm_exists = UserConfirmation.objects.filter(
                                                        user=user).exists()
            self.assertTrue(confirm_exists)

    def test_inactive_save(self):
        """ Test that form creates inactive user """
        form = SignupForm()
        form.cleaned_data = {'password1': 'password'}
        with patch.object(form, 'send_email'):
            user = form.save()
            self.assertFalse(user.is_active)

    def test_save_commit(self):
        """ Test that form creates inactive user """
        form = SignupForm()
        form.cleaned_data = {'password1': 'password'}
        with patch.object(form, 'send_email'):
            user = form.save(False)
            self.assertTrue(user.id is None)

