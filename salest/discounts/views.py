# Create your views here.
from django.views.generic.edit import FormView
from salest.discounts.forms import CartCodeDiscount
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


class CartDiscountView(FormView):
    template_name = 'discounts/cart_discount_form.html'
    form_class = CartCodeDiscount
    success_url = '/thanks/'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        return HttpResponseRedirect(reverse('cart:detail'))