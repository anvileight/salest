from django.conf.urls.defaults import url, patterns
from salest.payments.modules.dummy.processor import SucsessPaymentView

urlpatterns = patterns('salest.payments.modules.dummy.processor',
    url(r'^dummy/success/', SucsessPaymentView.as_view(),
                                                        name='dummy_success'),
)
