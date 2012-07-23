from django.conf.urls.defaults import url, patterns
from salest.payments.modules.trustcommerce.processor import SuccessPaymentView

urlpatterns = patterns('salest.payments.modules.trustcommerce.processor',
    url(r'^trustcommerce/success/', SuccessPaymentView.as_view(),
                                                name='trustcommerce_success'),
)
