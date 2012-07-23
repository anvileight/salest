"""
Test cases for signals
"""
from datetime import datetime, timedelta

from django_webtest import WebTest
from test_tools.utils import model_factory
from mock import patch, Mock

from salest.discounts.models import Discount
from salest.products.models import Product
from contextlib import nested


class DiscountManagerTestCase(WebTest):
    """ Test default discount manager methods """

    def test_get_active(self):
        """ Test that get_active method return active discounts """
        now = datetime.now()
        future = now + timedelta(days=7)
        past = now - timedelta(days=7)
        # invalid objects
        model_factory(Discount,
                      active=[False, True, True, True],
                      start_date=[now, future, now, None],
                      end_date=[now, now, past, past],
                      allowed_uses=[0, 0, 0, 0],
                      save=True)

        valid_objects = model_factory(Discount,
                      active=[True, True, True],
                      start_date=[now, past, None],
                      end_date=[now, future, now],
                      allowed_uses=[0, 10, 5],
                      save=True)

        actual_objects = Discount.objects.get_active()
        self.assertEqual(list(actual_objects), valid_objects,
                         valid_objects.get_diff(actual_objects, ordered=True))

