from django.db import models
from django.contrib.auth.models import User
from salest.products.models import Product, ProductVariation
from salest.core.utils import TimedeltaField


class Subscription(Product):
    """
    Extend model for subscription
    """
    pass


class Duration(ProductVariation):
    """
    Model for save time interval and users for this intrval
    """
    duration = TimedeltaField(default=0)
    users = models.ManyToManyField(User, related_name='membeship', blank=True)

    @property
    def subscription(self):
        """
        Property for return extend parent object
        """
        return self.product

    def get_price(self, quantity=1):
        """
        Overwrite method witch return price
        """
        return self.price

    def confirm(self, user):
        """
        Method add user to interval
        """
        self.users.add(user)
        self.save()
