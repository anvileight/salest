import uuid
from paypal.standard.forms import PayPalPaymentsForm
from salest.payments.models import Order
from salest.cart.models import Cart
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.views.generic.base import TemplateView
from django.utils.decorators import classonlymethod
from django.http import HttpResponseRedirect
import urllib
from paypal.standard.conf import POSTBACK_ENDPOINT


DEFAULT_FORMS = []

class ConfirmPaymentView(TemplateView):
    """
    View for confirmation purchase
    """
    template_name = 'redirect_confirm.html'

    def get_context_data(self):
        """
        Custom method
        """
        order = Order.objects.get(cart=self.request.cart)
        paypal_dict = {
            "at"
            "business": "salest@test.com",
            "amount": '{0:g}'.format(float(
                                       order.get_total_price_with_shiping())),
            "item_name": "Order: {0}".format(order.id),
            "item_number": order.id,
            "invoice": Order.generate_hash(order.id, order.get_total_price()),
            "return_url": 'http://' + Site.objects.get_current().domain,
            "notify_url": 'http://' + Site.objects.get_current(
                                              ).domain + reverse('paypal-ipn'),
            "cancel_return": "http://{0}".format(Site.objects.get_current()),
        }
        form = PayPalPaymentsForm(initial=paypal_dict)
        return {"form": form, 'order': order}


class SucsessPaymentView(TemplateView):
    """
    View for success purchase
    """
    template_name = 'success.html'

    def get_context_data(self):
        """
        Custom method
        """
        order = Order.objects.get(id=int(self.request.POST.get('item_number')))
        Cart.objects.remove_cart_from_session(self.request)
        order.confirm()
        return {'order': order}

    def post(self, request):
        return self.get(request)

