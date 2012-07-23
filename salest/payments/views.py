from django.contrib.formtools.wizard.views import SessionWizardView
from salest.accounts.models import Contact
from salest.cart.models import Cart
from salest.payments.payment_processor import get_payment_forms,\
    get_confirm_view
from salest.payments.forms import ChoiceShippingForm
from salest.payments.shipping_processor import get_shipping_methods
from django.conf import settings
from django.template.defaultfilters import slugify
from copy import copy
from django.contrib.auth.models import AnonymousUser


class PrePaymentWizard(SessionWizardView):
    """
    Form wizard for payment process
    """
    template_name = 'wizard.html'

    def __init__(self, payment_forms=None, *args, **kwargs):
        """
        Custom initiolization
        """
        super(PrePaymentWizard, self).__init__(*args, **kwargs)
        self.payment_forms = payment_forms
        self.cart = None
        self.contact = None
        self.order = None

    def get_context_data(self, form, **kwargs):
        context = SessionWizardView.get_context_data(self, form, **kwargs)
        context['passed'] = self.steps.all[:self.steps.index]
        context['not_passed'] = self.steps.all[self.steps.index:]
        data = {}
        form_data = self.get_all_cleaned_data()
        for step in context['passed']:
            data[step] = self.form_list[step](data=form_data)
        context['step_data'] = data
        return context

    def done(self, form_list, **kwargs):
        """
        Method called when all forms valid
        """
        if isinstance(self.request.user, AnonymousUser):
            self.contact = Contact.objects.create()
        else:
            self.contact = Contact.objects.get_or_create(
                                                     user=self.request.user)[0]
        self.cart = self.request.cart
        self.cart.contact = self.contact
        self.cart.save()

        self.order = self.cart.checkout()

        for form in form_list:
            if hasattr(form, 'save'):
                form.save(wizard=self)
        return get_confirm_view(
            self.get_payment_method_from_data(form_list))(
                            request=self.request).get(request=self.request)

    def get_payment_method_from_data(self, form_list):
        """
        Method return payment module name from forms data
        """
        for form in form_list:
            for key in form.data:
                if 'payment_method' in key:
                    return form.data[key]

    def get_payment_method_name_from_request(self):
        """
        Method return payment module name from request
        """
        for key in self.request.POST.keys():
            if 'payment_method' in key:
                return self.request.POST[key]

    def generate_choices(self, choice_data):
        """
        Generate Choices for shipping form
        """
        choices = []
        for module in settings.SHIPPING_MODULES:
            choices.append((module,
                            '{0} (${1})'.format(choice_data[module]['name'],
                                                choice_data[module]['price'])))
        return choices

    def post(self, *args, **kwargs):
        self.set_shipping_chises(self.request)
        return super(PrePaymentWizard, self).post(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        module_name = request.session.get('module_name', None)

        if module_name:
            del request.session['module_name']
        self.set_shipping_chises(request)
        return super(PrePaymentWizard, self).get(request, *args, **kwargs)

    def set_shipping_chises(self, request):
        cart = Cart.objects.get_or_create_from_request(request)
        for form in self.form_list.values():
            if form == ChoiceShippingForm:
                request.session['choice_data'] = get_shipping_methods(cart)
                form().set_choices(self.generate_choices(
                                            request.session['choice_data']))

    def add_paymet_form(self):
        """
        Add payment for to form wizard
        """
        module_name = self.get_payment_method_name_from_request()
        if module_name:
            self.request.session['module_name'] = module_name
            payment_forms = get_payment_forms(module_name, self.payment_forms)
            forms_count = self.steps.count
            forms_list = {}
            for counter, payment_form in enumerate(payment_forms):
                forms_list.update(
                                {unicode(forms_count + counter): payment_form})

            self.form_list.update(forms_list)

    def store_shipping_cost(self):
        for key in self.request.POST.keys():
            if 'shipping_method' in key:
                self.request.session['shipping_cost'] =\
                    self.request.session['choice_data'][
                                            self.request.POST[key]]['price']
                del self.request.session['choice_data']
                return

    def remove_payment_form_if_change(self):
        """
        If payment method is change we need delete previous payment form
        """
        old_module_name = self.request.session.get('module_name', None)
        current_module_name = self.get_payment_method_name_from_request()

        if old_module_name and current_module_name and\
                                    old_module_name != current_module_name:

            del self.request.session['module_name']
            self.form_list.pop(str(len(self.form_list) - 1))

    def process_shipping_address(self, form):
        if form.cleaned_data['is_billing']:
            self.initial_dict['Billing Address'] = form.cleaned_data
        else:
            self.initial_dict['Billing Address'] = {}
#        if form.

    def process_payment_method(self, form):
        payment_method = form.cleaned_data['payment_method']
        payment_forms = get_payment_forms(payment_method, self.payment_forms)
        if len(payment_forms):
            self.form_list.insert(4, 'Payment', payment_forms[0])
        elif 'Payment' in self.form_list:
            del self.form_list['Payment']
#        import pdb;pdb.set_trace()

    def get_cleaned_data_for_step(self, step):
        print SessionWizardView.get_cleaned_data_for_step(self, step)
        return SessionWizardView.get_cleaned_data_for_step(self, step)

    def process_custom_step(self, form):
        slug = slugify(self.steps.current).lower().replace('-', '_')
        fomr_step_process = 'process_' + slug
        if hasattr(self, fomr_step_process):
            getattr(self, fomr_step_process)(form)

    def process_step(self, form):
        """
        Custom method wich add payment forms from payment method to form
        wizard
        """
        self.store_shipping_cost()
        self.process_custom_step(form)
#        if self.steps.current == self.steps.last and self.steps.current != 'Confirm':
#            self.form_list['Confirm'] = Test
        return super(PrePaymentWizard, self).process_step(form)
