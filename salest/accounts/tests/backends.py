"""
Test cases for signals
"""
from django_webtest import WebTest
from django.contrib.auth.models import User
from test_tools.utils import model_factory

from salest.accounts.models import UserConfirmation
from salest.accounts.backends import ConfirmationUserBackend


class ConfirmationUserBackendTestCase(WebTest):
    """ Test accounts auth backends """

    def test_authenticate(self):
        """ Test that backend can authenticate user """
        code = 'test_code'
        expected_user = model_factory(User, save=True)
        model_factory(UserConfirmation, key=code,
                      user=expected_user, save=True)
        backend = ConfirmationUserBackend()
        self.assertEqual(expected_user, backend.authenticate(code))

    def test_authenticate_invalid(self):
        """
        Test that backend skip authentication of invalid user confirmations
        codes
        """
        expected_user = model_factory(User, save=True)
        model_factory(UserConfirmation, key='test_code',
                      user=expected_user, save=True)
        backend = ConfirmationUserBackend()
        self.assertTrue(backend.authenticate('another code') is None)
