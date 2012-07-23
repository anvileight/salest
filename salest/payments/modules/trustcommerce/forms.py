from salest.payments.forms import PaymentForm


class TrustCommercePaymentForm(PaymentForm):
    """
    Trust Comerce payment Form
    """
    def save(self, wizard=None):
        """
        Custom save for Trust Commerce Payment Form
        """
        wizard.request.session['payment_data'] = {
            'credit_number': self.cleaned_data['card_number'],
            'ccv': self.cleaned_data['ccv'],
            'expire': '{0}{1}'.format(self.cleaned_data['expire_month'],
                                      self.cleaned_data['expire_year'][-2:])}

        wizard.order.card_number = self.cleaned_data['card_number'][-4:]
        wizard.order.save()
        return wizard.order
