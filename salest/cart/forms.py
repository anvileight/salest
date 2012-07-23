"""
    Forms
"""

from django.forms import ModelForm, forms

from salest.cart.models import CartItem


class CartItemForm(ModelForm):
    """ CartItemForm  """

    class Meta:
        model = CartItem
        fields = ('quantity',)

#    def clean_quantity(self):
#        quantity = self.cleaned_data.get('quantity')
#        discounts = self.instance.discount.all()
#        if discounts:
#            can_add = True
#            allowed_quantity = None
#            for discount in discounts:
#                if quantity > discount.allowed_uses:
#                    can_add = False
#                    if allowed_quantity is None or \
#                                    allowed_quantity > discount.allowed_uses:
#                        allowed_quantity = discount.allowed_uses
#            if can_add:
#                discount.allowed_uses -= quantity - self.instance.quantity
#                discount.save()
#            else:
#                error_text = "select a smaller number of items,\
#                max = %s" % allowed_quantity
#                raise forms.ValidationError(error_text)
#        return quantity
