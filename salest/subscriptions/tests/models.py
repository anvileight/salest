from django_webtest import WebTest
from test_tools.utils import model_factory
from salest.subscriptions.models import Subscription, Duration
from django.contrib.auth.models import User


class DurationModelTestCase(WebTest):
    """
    Test Duration model
    """
    def test_subscription_property(self):
        """
        Test that property return write subscription
        """
        subscription = model_factory(Subscription, save=True)
        duration = model_factory(Duration, product=subscription)
        self.assertEqual(duration.subscription, subscription)

    def test_get_price_method(self):
        """
        Test that method return currect value
        """
        expected_value = 50
        duration = model_factory(Duration, price=expected_value)
        self.assertEqual(expected_value, duration.get_price())

    def test_confirm_method(self):
        """
        Test that method add user
        """
        user = model_factory(User, save=True)
        subscription = model_factory(Subscription, save=True)
        duration = model_factory(Duration, product=subscription, price=1,
                                                                    save=True)
        duration.confirm(user)
        self.assertTrue(user in duration.users.all())
