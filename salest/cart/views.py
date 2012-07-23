"""
Shop views.

"""
import json

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import View, DeleteView, DetailView, UpdateView
from django.shortcuts import get_object_or_404

from django.db.models.aggregates import Count, Sum
from salest.products.models import Product, ProductVariation
from salest.cart.models import Cart, CartItem
from salest.cart.forms import CartItemForm
from salest.discounts.forms import CartCodeDiscount
from salest.discounts.discounts import CartCodeMinOrderDiscount
from django.db.models import Count


class CartItemAddView(View):
    """ Add Product to cart """

    def get(self, request, product_id):
        """ get """
        cart = Cart.objects.get_or_create_from_request(request)
        product = get_object_or_404(ProductVariation, pk=product_id)
        cart.add_product(product)
        return HttpResponseRedirect(request.GET.get('next',
                                                    reverse('cart:detail')))


class CartItemUpdateView(UpdateView):
    """ CartItemUpdateView """
    form_class = CartItemForm
    model = CartItem
    success_url = reverse_lazy('cart:detail')


class CartItemDeleteView(DeleteView):
    """ CartItemDeleteView """
    model = CartItem
    success_url = reverse_lazy('cart:detail')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        cart = self.object.cart
        self.object.delete()
        cart.revalidate_discounts()
        return HttpResponseRedirect(self.get_success_url())


class CartDetailView(DetailView):
    """ CartDetailView """
    context_object_name = 'cart'

    def get_context_data(self, **kwargs):
        context = super(CartDetailView, self).get_context_data(**kwargs)
        context['cart_discount_form'] = CartCodeDiscount()
        return context

    def post(self, request):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        form = CartCodeDiscount(request.POST)
        if form.is_valid():
            discount = CartCodeMinOrderDiscount()
            if discount.is_valid(form.cleaned_data['code'],
                               context['object'].get_items_price()):
                context['object'].add_discount(discount.discount)
                return HttpResponseRedirect(reverse('cart:detail'))
            form.errors['code'] = discount.errors
        context['cart_discount_form'] = form
        return self.render_to_response(context)

    def get_object(self, queryset=None):
        """ Return new or existing cart """
        self.request.cart = Cart.objects.annotate(quantity=Sum('items__quantity')
                      ).select_related().prefetch_related(
                      'items', 'discount', 'items__discount',
                      'items__product', 'items__product__product',
                      ).get(id=self.request.cart.id)
        return self.request.cart

