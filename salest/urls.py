from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from salest.payments.payment_processor import url_lookup

admin.autodiscover()


urlpatterns = patterns('',
    url(r'^accounts/', include('salest.accounts.urls', namespace='accounts')),
    url(r'^products/', include('salest.products.urls', namespace='products')),
    url(r'^shop/', include('salest.cart.urls', namespace='cart')),
    url(r'^payment/', include('salest.payments.urls', namespace='payment')),
    url(r'^subscription/', include('salest.subscriptions.urls',
                                                    namespace='subscription')),
    url(r'^discount/', include('salest.discounts.urls',
                                                    namespace='discount')),
    #TODO: temporary
    url(r'^$', include('salest.products.urls', namespace='products')),
)

urlpatterns += patterns('',
#    url(r'^success/$', 'paypal.standard.ipn.views.ipn', name='success'),
    url(r'^something/hard/to/guess/', include('paypal.standard.ipn.urls')),
)

look_up_urls = url_lookup()
if look_up_urls:
    urlpatterns += look_up_urls
