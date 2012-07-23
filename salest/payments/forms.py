import datetime
import calendar
import re

from django import forms
from django.conf import settings

CARD_CHOICES = (('visa', 'Visa'),
                 ('mastercard', 'Mastercard')
                )


def generate_year_list():
    """ Generate years from now to 10 next years """
    current = datetime.datetime.now().year
    return tuple((year, year) for year in range(current, current + 10))


def generate_month_list():
    """ Generate month choices """
    months = []
    for month in range(1, 13):
        month = str(month)
        if len(month) == 1:
            month = '0{0}'.format(month)
        months.append((month, month))
    return months


def validate_card_number(number):
    """ Function for validation Credit Card number """
    double = 0
    sum_numbers = 0
    for num in range(len(number) - 1, -1, -1):
        for each_num in str((double + 1) * int(number[num])):
            sum_numbers = sum_numbers + int(each_num)
        double = (double + 1) % 2
    return ((sum_numbers % 10) == 0)


def generate_payment_methods():
    """
    Method for generation methods of payment
    """
    methods = []
    for method in settings.PAYMENT_MODULES:
        methods.append((method, method))
    return methods


class ChoicePaymentForm(forms.Form):
    """
    Form for choice payment mentod
    """
    payment_method = forms.ChoiceField(choices=generate_payment_methods())


SHIPPING_MODULES = None


class ChoiceShippingForm(forms.Form):
    """
    Form for choice shipping method
    """
    shipping_method = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        if SHIPPING_MODULES:
            self.base_fields['shipping_method'] = forms.ChoiceField(
                                                    choices=SHIPPING_MODULES)

        return super(ChoiceShippingForm, self).__init__(*args, **kwargs)

    def set_choices(self, choices):
        global SHIPPING_MODULES
        SHIPPING_MODULES = choices

        self.base_fields['shipping_method'] = forms.ChoiceField(
                                                    choices=SHIPPING_MODULES)

    def save(self, wizard):
        order = wizard.order
        order.shipping_method = self.cleaned_data['shipping_method']
        order.shipping_price = wizard.request.session['shipping_cost']
        order.save()


class PaymentForm(forms.Form):
    """
    Form for pyment informations
    """
    credit_type = forms.ChoiceField(choices=CARD_CHOICES)
    card_number = forms.CharField(max_length=20,
                        widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    ccv = forms.CharField(max_length=4,
                        widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    expire_month = forms.ChoiceField(choices=generate_month_list())
    expire_year = forms.ChoiceField(choices=generate_year_list())
    order_note = forms.Textarea()

    def validate_expire_date(self):
        """ Validate expire date """
        month = int(self.cleaned_data['expire_month'])
        year = int(self.cleaned_data['expire_year'])
        max_day = calendar.monthrange(year, month)[1]

        if datetime.date.today() > datetime.date(year=year, month=month,
                                                                day=max_day):
            return False
        return True

    def clean(self, *args, **kwargs):
        """ Custon form clean """
        data = super(PaymentForm, self).clean(*args, **kwargs)
        if not self.validate_expire_date():
            raise forms.ValidationError('Your card has expired.')

        return data

    def clean_card_number(self):
        """ Custiom clean Credit Card Number """
        credit_number = re.sub(r'[^0-9]', '', self.cleaned_data['card_number'])

        if not validate_card_number(credit_number):
            raise forms.ValidationError('Enter a valid credit card number.')
        return credit_number

    def clean_ccv(self):
        """ Custom clean of card CCV """
        try:
            int(self.cleaned_data['ccv'])
        except ValueError:
            raise forms.ValidationError('Invalid ccv.')
        else:
            return self.cleaned_data['ccv'].strip()

class ConfirmForm(forms.Form):
    agree = forms.BooleanField(required=True)
