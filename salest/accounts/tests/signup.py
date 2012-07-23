"""
Test cases for signup process
"""
from django_webtest import WebTest
from django.core.urlresolvers import reverse
from django.contrib.auth import SESSION_KEY
from django.contrib.auth.models import User
from test_tools.utils import get_fake_email, model_factory
from mock import patch, Mock

from salest.core.models import EmailTemplate
from salest.accounts.models import UserConfirmation
from salest.accounts.views import ConfirmationView


class ViewTestCase(WebTest):
    """ Test sign up form view """

    def test_view(self):
        """ Test signup view process """
        model_factory(EmailTemplate, template_key='invitation_email',
                      save=True)
        resp = self.app.get(reverse('accounts:signup'))
        form = resp.form
        form['username'] = 'john.smith'
        form['password1'] = 'password'
        form['password2'] = 'password'
        form['email'] = get_fake_email()
        response = form.submit()
        self.assertEqual(response.status, '302 FOUND')

    def test_confirm_view(self):
        """ Test confirmation view """
        confirm_key = 'some_key'
        user = model_factory(User, save=True)
        model_factory(UserConfirmation, key=confirm_key, user=user, save=True)
        response = self.app.get(reverse('accounts:confirm'), params={
                                                        'key': confirm_key})
        self.assertEqual(self.app.session[SESSION_KEY], user.id)
        self.assertEqual(response.status, '200 OK')

    def test_confirm_fail_view(self):
        """ Test confirmation failed """
        with patch('salest.accounts.views.ConfirmationView.process_user',
                   Mock(return_value=None)):
            response = self.app.get(reverse('accounts:confirm'))
        self.assertFalse(SESSION_KEY in self.app.session)
        self.assertEqual(response.status, '200 OK')

    def test_confirm_process_user(self):
        """ Test confirmation process user """
        view = ConfirmationView()
        user = model_factory(User)
        with patch.object(view, 'get_auth_user', Mock(return_value=user)):
            user = view.process_user()
            self.assertTrue(user.is_active)

    def test_confirm_process_no_user(self):
        """ Test confirmation process user with non authenticated user """
        view = ConfirmationView()
        with patch.object(view, 'get_auth_user', Mock(return_value=None)):
            user = view.process_user()
            self.assertTrue(user is None)

    def test_get_auth_user(self):
        """ Test get auth user """
        view = ConfirmationView()
        confirm_key = 'some_key'
        view.request = Mock(GET={'key': confirm_key})
        with patch(
                'salest.accounts.backends.ConfirmationUserBackend.authenticate'
                   ) as auth:
            view.get_auth_user()
            auth.assert_called_once_with(confirmation_code=confirm_key)
