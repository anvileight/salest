"""
    This file consists of example models for e-comerce app based on Salest Core
    and Django.
    Every class should extend core class with basic interfaces.
"""
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from salest.products.models import Product
from salest.core.utils import get_secure_key
from salest.cart.models import Cart


class Contact(models.Model):
    """ Extended Profile Class """
    user = models.OneToOneField(User, blank=True, null=True)

    def __init__(self, *args, **kwargs):
        self.date = datetime.now().date()
        super(self.__class__, self).__init__(*args, **kwargs)

    def __unicode__(self):
        try:
            return self.user.username
        except AttributeError:
            return 'Anonimus'

    def has_discount(self):
        """
        This method checks for the existence of discounts for this user and
        his categories
        """
        return bool(self.discount_set.count())

    def get_discounts_list(self):
        """ This method checks for the existence of discounts for this user and
            his categories """
        return self.discount_set.all()

    @property
    def cart(self):
        """ Return current active cart """
        try:
            return self.carts.filter(is_active=True).get()
        except Cart.DoesNotExist:
            return None


class AddressManager(models.Manager):
    """ Custom address manager """
    def get_shipping_address_by_contact(self, contact):
        """ Get shipping address by contact """
        try:
            return self.get_query_set().get(contact=contact, is_shipping=True)
        except Address.DoesNotExist:
            return None

    def get_billing_address_by_contact(self, contact):
        """ Get billing address by contact """
        try:
            return self.get_query_set().get(contact=contact, is_billing=True)
        except Address.DoesNotExist:
            return None


class Address(models.Model):
    """ Address model with flags for default billin and shipping address """
    contact = models.ForeignKey(Contact)
    street1 = models.CharField(max_length=80)
    street2 = models.CharField(max_length=80, blank=True)
    addressee = models.CharField(max_length=80)
    state = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=30)
    country = models.CharField(max_length=255)
    is_shipping = models.BooleanField(default=False)
    is_billing = models.BooleanField(default=False)

    objects = AddressManager()

    ADDRESS_FIELDS = ['street1', 'street2', 'addressee', 'state',
                      'city', 'postal_code', 'country']


class Invitation(models.Model):
    """ Extended Invitation Class """

    first_name = models.CharField("First Name", max_length=200)
    last_name = models.CharField("Last Name", max_length=200)
    email = models.EmailField("Email")
    hash_key = models.CharField("Invitation Key",
                                max_length=200,
                                blank=True,
                                null=True)
    is_active = models.BooleanField("Active", default=True)

    def __unicode__(self):
        """ """
        return "%s %s invitation" % (self.first_name, self.last_name)

    def __init__(self, *args, **kwargs):
        """ Custom init method """
        super(Invitation, self).__init__(*args, **kwargs)
        self.set_hash_key()

    def set_hash_key(self):
        """ This method generate and set hash key based on """
        self.hash_key = get_secure_key(self.email)
        return True


class Wishlist(models.Model):
    """ Extended Wishlist Class """
    user = models.OneToOneField(Contact)
    products = models.ManyToManyField(Product, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        """ unicode """
        return "%s's wishlist" % (self.user.user.username)

    def add_item(self, product_item):
        """ this method add item to wishlist """
        self.products.add(product_item)
        return self

    def remove_item(self, product_item):
        """ this method remove item from wishlist """
        self.products.remove(product_item)
        return self

    def get_wished_items(self):
        """ this method returns list of wished items """
        return self.products.all()

    def get_url(self):
        """ this method returns redirect URL """
        return reverse('wishlist', args=[self.id])


class UserConfirmation(models.Model):
    """ This class should store relation betwwin """
    user = models.ForeignKey(User)
    key = models.CharField("Confirmation Key",
                            max_length=200)

# keep this. It protect recursive imports with listeners
from salest.accounts import listeners
