import tclink
from salest.payments.modules.trustcommerce.forms import\
                                                    TrustCommercePaymentForm
from django.core.urlresolvers import reverse
from salest.payments.models import Order
from salest.cart.models import Cart
from django.conf import settings
from django.views.generic.base import TemplateView

DEFAULT_FORMS = [TrustCommercePaymentForm]


class ConfirmPaymentView(TemplateView):
    """
    View for confirmation purchase
    """
    template_name = 'confirm.html'

    def get_context_data(self):
        """
        Custom method
        """
        sucsees_url = reverse('trustcommerce_success')
        order = Order.objects.get(cart=self.request.cart)
        return {'module_success_url': sucsees_url, 'order_id': order.id}


class SuccessPaymentView(TemplateView):
    """
    View for success purchase
    """
    template_name = 'success.html'

    def get_context_data(self):
        order = Order.objects.get(id=self.request.POST.get('order_id'))
        result = tclink.send(prepere_payment_information(order,
                                        self.request.session['payment_data']))

        del self.request.session['payment_data']

        status = result['status']

        if status == 'approved':
            order.confirm()
            Cart.objects.remove_cart_from_session(self.request)
            return {'order': order}

        self.template_name = 'payment_error.html'
        return {'message': get_error_message(result)}

    def post(self, request):
        """
        That means as post request work like get request
        """
        return self.get(request)


def prepere_payment_information(order, payment_data):
    amount = unicode((order.get_total_price() * 100))
    transactionData = {
        # account data
        'custid': settings.TRUSTCOMMERCE_USER_ID,
        'password': settings.TRUSTCOMMERCE_PASSWORD,
        'demo': settings.TRUSTCOMMERCE_IS_DEMO_PAYMENT,

        # Customer data
        'name': u'{0} {1}'.format(order.cart.contact.user.first_name,
                                        order.cart.contact.user.last_name),
        'address1': order.billing_street1,
        'city': order.billing_city,
        'state': order.billing_state,
        'zip': order.billing_postal_code,
        'country': order.billing_country,
        'phone': "",
        # other possibiliities include email, ip, offlineauthcode, etc

        # transaction data
        'media': 'cc',
        'action': 'sale',
        'amount': amount,
        'cc': payment_data['credit_number'],
        'exp': payment_data['expire'],
        'cvv': payment_data['ccv'],
        'avs': settings.TRUSTCOMMERCE_AVS,
        'ticket': u'Order: %s' % order.id,
        'operator': 'Salest'
    }

    for key, value in transactionData.items():
        if isinstance(value, unicode):
            transactionData[key] = value.encode('utf8', "ignore")

    return transactionData


def get_error_message(result):
    status = result['status']
    if status == 'decline':
        return u'Transaction was declined.  Reason: {0}'.format(
                                                        result['declinetype'])
    elif status == 'baddata':
        return u'Improperly formatted data. Offending fields: {0}'.format(
                                                        result['offenders'])
    elif status == 'error':
        return u'An error occurred: {0}'.format(result['errortype'])
