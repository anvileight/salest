from django.conf.urls.defaults import patterns, url
from salest.discounts.views import CartDiscountView


urlpatterns = patterns('',
    url(r'^cart/$', CartDiscountView.as_view(), name='cart'),
)
