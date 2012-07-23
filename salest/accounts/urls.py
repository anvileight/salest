from django.conf.urls.defaults import patterns, url
from django.views.generic import TemplateView

from salest.core.views import AddItemView, RemoveItemView
from salest.products.models import Product

from salest.accounts.models import Wishlist
from salest.accounts.views import ConfirmationView
from salest.accounts.forms import SignupForm
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView


urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login',
                        {'template_name': 'login.html'}, name="login"),

    url(r'^logout/$', 'django.contrib.auth.views.logout',
                        {'next_page': '/'}, name="logout"),

)

urlpatterns += patterns('accounts',
    url(r'^signup/', CreateView.as_view(form_class=SignupForm,
                                        success_url='/accounts/check_mail',
                                        template_name='accounts/signup.html'),
        name="signup"),
    (r'^check_mail/', TemplateView.as_view(
                            template_name='accounts/check_mail.html')),
    url(r'^confirm/', ConfirmationView.as_view(
                            template_name='accounts/mail_confirmation.html'),
                            name="confirm"),
    url(r'^product/(?P<item_pk>\d+)/add_to/wishlist/(?P<list_pk>\d+)/$',
                AddItemView.as_view(item_class=Product,
                                    list_class=Wishlist,
                                    success_url='/'),
                name='add_to_wishlist'),
    url(r'^product/(?P<item_pk>\d+)/remove_from/wishlist/(?P<list_pk>\d+)/$',
                RemoveItemView.as_view(item_class=Product,
                                       list_class=Wishlist,
                                       success_url='/'),
                name='remove_wished_item'),
    url(r'^wishlist/(?P<pk>\d+)/$', DetailView.as_view(
                                        model=Wishlist,
                                        context_object_name="object_details",
                                        ), name="wishlist"),

)
