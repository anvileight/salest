from django import forms

class CartCodeDiscount(forms.Form):
    code = forms.CharField(label='Discount Code', required=True)

        

