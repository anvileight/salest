""" This file would consist of Forms for accounts module  """

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from salest.core.utils import get_secure_key
from salest.accounts.models import UserConfirmation, Address, Contact
from salest.core.models import EmailTemplate
from django.contrib.sites.models import Site


class InstanceSaveCommitMixin(object):
    def save(self, commit=True):
        if commit:
            self.instance.save()
        return self.instance


class BaseAddressForm(forms.ModelForm, InstanceSaveCommitMixin):
    """ Base Address form """

    contact = None

    class Meta(object):
        """ Metaclass for model form """
        model = Address

    def save(self, wizard=None, commit=True):
        forms.ModelForm.save(self, commit=False)
        if wizard is not None:
            self.instance.contact = wizard.contact
        InstanceSaveCommitMixin.save(self, commit)
        return self.instance


class ShippingAddressForm(BaseAddressForm, InstanceSaveCommitMixin):
    """ Shipping Address Form """

    class Meta(BaseAddressForm.Meta):
        """ Metaclass for model form """
        exclude = ('contact', 'is_shipping')

    def save(self, commit=True, wizard=None):
        address_inst = Address.objects.get_shipping_address_by_contact(
                                                            wizard.contact)
        if address_inst:
            self.instance = address_inst

        BaseAddressForm.save(self, wizard=wizard, commit=False)
        self.instance.is_shipping = True
        InstanceSaveCommitMixin.save(self, commit=commit)
        return self.instance


class BillingAddressForm(BaseAddressForm):
    """ Billing Address Form """

    class Meta(BaseAddressForm.Meta):
        """ Metaclass for model form """
        exclude = ('contact', 'is_billing', 'is_shipping')

    def save(self, commit=True, wizard=None):
        address_inst = Address.objects.get_billing_address_by_contact(
                                                            wizard.contact)
        if address_inst:
            self.instance = address_inst

        BaseAddressForm.save(self, wizard=wizard, commit=False)
        self.instance.is_billing = True
        InstanceSaveCommitMixin.save(self, commit=commit)
        return self.instance


class SignupForm(UserCreationForm, InstanceSaveCommitMixin):
    """ SignupForm """
    email = forms.EmailField(label="E-mail", max_length=75)

    class Meta(object):
        """ Metaclass for model form """
        model = User
        fields = ("username", "email", )

    def send_email(self):
        """
        This method should send email to just registered User with
        confirmation link
        """
        key = get_secure_key(self.instance.email)
        site = Site.objects.get_current()
        UserConfirmation.objects.create(user=self.instance,
                                        key=key)
        context = {'site': site,
                   'key': key
        }
        kw_params = {'template_key': 'invitation_email',
                     'context': context,
                     'emails': [self.instance.email]
        }
        EmailTemplate.send(**kw_params)

    def save(self, commit=True):
        super(SignupForm, self).save(commit=False)
        self.instance.is_active = False
        InstanceSaveCommitMixin.save(self, commit=commit)
        self.send_email()
        return self.instance
