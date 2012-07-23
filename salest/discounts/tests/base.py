from django_webtest import WebTest
from mock import Mock, patch
from salest.discounts.base import DiscountTypeBase


class DiscountTypeBaseTestCase(WebTest):

    def test_get_qs(self):
        base = DiscountTypeBase()
        qs = Mock()
        self.assertEqual(base.get_qs(qs), qs)

