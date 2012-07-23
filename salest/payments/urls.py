from django.conf.urls.defaults import patterns, url, include
from salest.accounts.forms import ShippingAddressForm, BillingAddressForm
from salest.payments.views import PrePaymentWizard
from salest.payments.forms import ChoicePaymentForm, ChoiceShippingForm,\
    ConfirmForm

pre_payment_wizard = PrePaymentWizard.as_view((
                                  ('Shipping Address', ShippingAddressForm ),
                                  ('Billing Address', BillingAddressForm),
                                  ('Shipping Method', ChoiceShippingForm),
                                  ('Payment Method', ChoicePaymentForm),
                                  ('Confirm', ConfirmForm)))

urlpatterns = patterns('salest.payments.views',
    url(r'^$', pre_payment_wizard, name='pre_payment'),
#    url(r'^success/$', 'success', name='success'),
)

