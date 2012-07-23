from django.conf.urls.defaults import patterns, url

from salest.products.models import Product
from django.views.generic.detail import DetailView
from salest.products.views import ProductListView, CatalogueListView, \
    CategoryListView, ProductDetailView

urlpatterns = patterns('',
    url(r'^$', ProductListView.as_view(), name='list'),

    url(r'^(?P<pk>\d+)/$', ProductDetailView.as_view(), name='details'),

    url(r'^category/(?P<slug>\w+)/$', CategoryListView.as_view(),
                                    name="category_details"),
    url(r'^catalogue/', CatalogueListView.as_view(), name='catalogue')
)
