from django.conf.urls.defaults import patterns, url
from django.views.generic import DetailView

from salest.cart.views import CartItemAddView, CartItemUpdateView, \
    CartItemDeleteView, CartDetailView

from salest.discounts.models import Discount

urlpatterns = patterns('',
    url(r'^$', CartDetailView.as_view(), name='detail'),

    url(r'^cart/add/(?P<product_id>\d+)/$', CartItemAddView.as_view(),
                                            name='add'),
    url(r'^cart/edit/(?P<pk>\d+)/$', CartItemUpdateView.as_view(),
                                            name='edit'),
    url(r'^cart/delete/(?P<pk>\d+)/$', CartItemDeleteView.as_view(),
                                            name='delete'),

    url(r'^users_discount/details/(?P<pk>\d+)/$',
                            DetailView.as_view(
                                    model=Discount,
                                    context_object_name="object_details",
                                ), name='users_discount_details'),
    url(r'^products_discount/details/(?P<pk>\d+)/$',
                            DetailView.as_view(
                                    model=Discount,
                                    context_object_name="object_details",
                                ), name='products_discount_details'),
    url(r'^products_categories_discount/details/(?P<pk>\d+)/$',
                            DetailView.as_view(
                                    model=Discount,
                                    context_object_name="object_details",
                            ), name='products_categories_discount_details'),

)
