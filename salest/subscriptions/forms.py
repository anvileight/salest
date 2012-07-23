from django import forms
from salest.subscriptions.models import Subscription, Duration


def generaet_member_choice():
    """
    Method for generate types of members
    """
    choices = []
    for member_type in Subscription.objects.all():
        choices.append((member_type.id, member_type.name))
    return choices


def generate_duration_choice(subscription_id):
    """
    Method for generate duration for member type
    """
    choice = []
    for duration in Duration.objects.filter(product__id=subscription_id):
        choice.append((duration.id, "{0} days for ${1}".format(
                                                    duration.duration.days,
                                                    duration.price)
                     ))
    return choice


class MemberForm(forms.Form):
    """
    Form for select member type
    """
    member_type = forms.ChoiceField(widget=forms.RadioSelect,
                                            choices=generaet_member_choice())


class DurationForm(forms.Form):
    """
    Form for select duration type
    """
    duration_type = forms.ChoiceField(widget=forms.RadioSelect,
                                            choices=[])
