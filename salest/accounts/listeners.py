""" There should be stored signals listeners. """

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from salest.accounts.models import Invitation, Contact, Wishlist
from salest.core.models import EmailTemplate


@receiver(post_save, sender=User, dispatch_uid="user_saved")
def user_saved(sender, instance, created, **kwargs):
    """ This function creates Profile for every new User """
    if created:
        profile = Contact.objects.create(user=instance)
        Wishlist.objects.create(user=profile)


@receiver(post_save, sender=Invitation, dispatch_uid="invite_notification")
def invite_notification(sender, instance, **kwargs):
    """ This function should notify invited person by email. """
    context = {'hash_key': instance.hash_key, }
    params = {'template_key': 'invitation_email',
                     'context': context,
                     'emails': [instance.email, ]}

    return EmailTemplate.send(kw_params=params)
