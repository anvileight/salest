from django_webtest import WebTest
from test_tools.utils import model_factory
from salest.subscriptions.models import Subscription, Duration
from salest.subscriptions.forms import generaet_member_choice,\
    generate_duration_choice


class FormsTestCase(WebTest):
    """
    Tests for forms and forms methods
    """
    def test_generaet_member_choice_method(self):
        """
        Test that method generate currect choices
        """
        subscription = model_factory(Subscription, save=True)
        expected_value = [(subscription.id, subscription.name)]
        current_value = generaet_member_choice()
        self.assertEqual(expected_value, current_value)

    def test_generate_duration_choice_method(self):
        """
        Test that method generate currect choices
        """
        subscription = model_factory(Subscription, save=True)
        duration = model_factory(Duration, product=subscription, price=12,
                                                                    save=True)
        expected_value = [(duration.id, "{0} days for ${1}.00".format(
                                                    duration.duration.days,
                                                    duration.price))]
        current_value = generate_duration_choice(subscription.id)
        self.assertEqual(expected_value, current_value)
