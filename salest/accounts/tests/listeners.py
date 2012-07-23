"""
Test cases for signals
"""
from django_webtest import WebTest
from django.contrib.auth.models import User
from test_tools.utils import model_factory
from mock import patch

from salest.accounts.models import Contact, Wishlist, Invitation


class TestCase(WebTest):
    """ Test accounts signals """

    def test_profile_creation(self):
        """ Test that profile creates """
        user = model_factory(User)
        user.save()
        profile_exists = Contact.objects.filter(user=user).exists()
        self.assertTrue(profile_exists)

    def test_profile_not_created_on_up(self):
        """ Test that profile not created if user updated """
        user = model_factory(User, save=True)
        user.username = 'test'
        user.save()
        profiles = Contact.objects.filter(user=user).count()
        self.assertTrue(profiles == 1)

    def test_whishlist_creation(self):
        """ Test that whishlist creates """
        user = model_factory(User)
        user.save()
        profile_exists = Wishlist.objects.filter(user=user.contact).exists()
        self.assertTrue(profile_exists)

    def test_invite_notification(self):
        """ Test that email sent when invite was created """
        invite = model_factory(Invitation)
        with patch('salest.core.models.EmailTemplate.send') as email_meth:
            invite.save()
            self.assertEqual(email_meth.call_count, 1)
