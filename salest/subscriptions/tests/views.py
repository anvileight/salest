from django_webtest import WebTest
from mock import patch, Mock
from test_tools.utils import model_factory
from salest.subscriptions.views import NotMemberFormWizard
from django.test.client import RequestFactory
from salest.subscriptions.models import Duration, Subscription
from contextlib import nested
from django.contrib.auth.models import User


class NotMemberFormWizardTestCase(WebTest):
    """
    Test that wizzard works currect
    """
    def test_get_member_type_from_request(self):
        """
        Test that method can return member type
        """
        expected_value = '1'
        request = RequestFactory().post('/', {'member_type': expected_value})
        wizard = NotMemberFormWizard()
        wizard.request = request
        current_value = wizard._get_member_type_from_request()
        self.assertEqual(expected_value, current_value)

    def test_process_step(self):
        """
        Test that method can call _get_member_type_from_request method
        """
        subscription = model_factory(Subscription, save=True)
        model_factory(Duration, price=10, product=subscription, save=True)
        request = RequestFactory().post('/', {'member_type': subscription.id})
        wizard = NotMemberFormWizard()
        wizard.form_list = {'0': Mock(), '1':
                        Mock(base_fields={'duration_type': Mock(choices=[])})}
        wizard.request = request
        with patch(
            'salest.subscriptions.views.NotMemberFormWizard._get_member_type_from_request',
                                Mock(return_value=subscription.id)) as member:
            wizard.process_step(Mock())
            member.assert_called_once_with()

    def test_done(self):
        """
        Test that method call add_product method
        """
        subscription = model_factory(Subscription, save=True)
        duration = model_factory(Duration, price=10, items_in_stock=12,
                                 product=subscription, save=True)
        form_list = {'0': Mock(), '1': Mock()}
        request = RequestFactory()
        request.user = model_factory(User, save=True)
        wizard = NotMemberFormWizard()
        wizard.request = request
        with nested(
            patch('django.contrib.formtools.wizard.views.WizardView.get_all_cleaned_data',
                  Mock(return_value={'duration_type': duration.id}))):
            wizard.done(form_list)
