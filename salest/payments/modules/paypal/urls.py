from django.conf.urls.defaults import url, patterns
from salest.payments.modules.paypal.processor import SucsessPaymentView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = patterns('salest.payments.modules.paypal.processor',
    url(r'^paypal/success/', csrf_exempt(SucsessPaymentView.as_view()),
                                                        name='paypal_success'),
)
