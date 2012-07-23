from django.core.urlresolvers import reverse
from salest.cart.models import Cart
from salest.payments.models import Order
from salest.payments.modules.dummy.forms import DummyPaymentForm
from django.views.generic.base import TemplateView

DEFAULT_FORMS = [DummyPaymentForm]


class ConfirmPaymentView(TemplateView):
    """
    View for confirmation purchase
    """
    template_name = 'confirm.html'

    def get_context_data(self):
        """
        Custom method
        """
        sucsees_url = reverse('dummy_success')
        order = Order.objects.get(
                            cart=self.request.cart)
        return {'module_success_url': sucsees_url, 'order_id': order.id}


class SucsessPaymentView(TemplateView):
    """
    View for success purchase
    """
    template_name = 'success.html'

    def get_context_data(self):
        """
        Custom method
        """
        order = Order.objects.get(id=self.request.POST.get('order_id'))
        Cart.objects.remove_cart_from_session(self.request)
        order.confirm()
        return {'order': order}

    def post(self, request):
        """
        That means as post request work like get request
        """
        return self.get(request)
