from salest.payments.forms import PaymentForm


class DummyPaymentForm(PaymentForm):
    """
    Dummy payment form
    """
    def save(self, wizard):
        """
        Dummy save methot that save last for numbers of credit card
        """
        order = wizard.order
        order.card_number = self.cleaned_data['card_number'][-4:]
        order.save()
        return order
