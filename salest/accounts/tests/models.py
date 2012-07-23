"""
Test cases for signup process
"""
from datetime import datetime

from django_webtest import WebTest
from django.contrib.auth.models import User
from test_tools.utils import model_factory

from salest.accounts.models import Contact, Invitation, Wishlist
from salest.discounts.models import Discount


class ProfileTestCase(WebTest):
    """ Test models """

    def test_unicode(self):
        """ Test that profile return valid username """
        expeced_value = 'test_username'
        user = model_factory(User, username=expeced_value, save=True)
        profile = Contact.objects.get(user=user)
        self.assertEqual(expeced_value, str(profile))
        profile = model_factory(Contact, save=True)
        self.assertEqual('Anonimus', str(profile))

    def test_has_discount(self):
        """ Test has_discount method """
        discount = model_factory(Discount, end_date=datetime.now(),
                                 start_date=datetime.now(),
                                 save=True)
        user = model_factory(User, save=True)
        self.assertFalse(user.contact.has_discount())
        discount.valid_users.add(user.contact)
        self.assertTrue(user.contact.has_discount())
    
    def test_get_discounts(self):
        """ Test has_discount method """
        expected = model_factory(Discount, end_date=datetime.now(),
                                 start_date=datetime.now(),
                                 save=True)
        user = model_factory(User, save=True)
        expected.valid_users.add(user.contact)
        self.assertEqual([expected], list(user.contact.get_discounts_list()))

class InvitationTestCase(WebTest):
    def test_unicode(self):
        expected = 'first_test last_test invitation'
        inv = model_factory(Invitation, first_name='first_test',
                            last_name='last_test')
        self.assertEqual(expected, str(inv))

class WishlistTestCase(WebTest):

    def test_unicode(self):
        expected = "test_username's wishlist"
        user = model_factory(User, username='test_username', save=True)
        contact = Contact.objects.get(user=user)
        wish = Wishlist.objects.get(user=contact)
        self.assertEqual(expected, str(wish))

