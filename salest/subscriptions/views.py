from django.http import HttpResponseRedirect
from salest.subscriptions.decorators import for_member_only
from django.contrib.formtools.wizard.views import SessionWizardView
from salest.subscriptions.forms import generate_duration_choice
from salest.cart.models import Cart
from salest.subscriptions.models import Duration
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template


@for_member_only()
def member(request):
    """
    View only for members
    """
    member_type = request.user.membeship.all()[0]
    return direct_to_template(request, 'member.html',
                                                {'member_type': member_type})


class NotMemberFormWizard(SessionWizardView):
    """
    Wizard witch offers by some membership
    """
    template_name = 'not_a_member.html'

    def done(self, form_list, **kwargs):
        """
        Custom done method witch add membership data in cart
        """
        data = self.get_all_cleaned_data()
        duration = Duration.objects.get(id=data['duration_type'])
        cart = Cart.objects.get_or_create_from_request(self.request)
        cart.add_product(duration)
        return HttpResponseRedirect(reverse('cart:detail'))

    def _get_member_type_from_request(self):
        """
        Method witch get member type from request
        """
        for key in self.request.POST.keys():
            if 'member_type' in key:
                return self.request.POST[key]

    def process_step(self, form):
        """
        Custom process step method witch rewrite choices in DurationForm for
        current type of member type
        """
        subscription_id = self._get_member_type_from_request()
        if subscription_id:
            choices = generate_duration_choice(subscription_id)
            self.form_list['1'].base_fields['duration_type'].choices = choices

        return super(NotMemberFormWizard, self).process_step(form)
