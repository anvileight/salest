"""
Discount models
"""
from datetime import datetime

from django.db import models
from django.db.models import Q

from salest.products.interfaces import ProductInterface
from salest.discounts.validators import DiscountRegistr
from decimal import Decimal


class DiscountManager(models.Manager):
    def get_active(self):
        now = datetime.now()
        return self.filter(
           Q(start_date__lte=now, end_date__gte=now) |
           Q(start_date__isnull=True, end_date__gte=now) |
           Q(start_date__isnull=True, end_date__isnull=True)).filter(
                                                active=True)


class DiscountValidatorManager(models.Manager):
    pass

#    def process_qs(self, method, qs, **kw):
#        try:
#            validators = Validators.discounts[method]
#        except KeyError:
#            raise KeyError('Discount "{0}" not register.').format(method)
##        q_objects = []
##        for validator in validators:
##            validator = validator(qs)
###            func_kw = get_func_kwargs(validator.get_q_object, **kw)
##            q_object = validator.get_q_object(**func_kw)
##            qs = validator.qs
##            q_objects.append(q_object)
##        q_object = reduce(operator.and_, q_objects)
##        return qs, q_object
#
#    def by_list(self, methods, **kwargs):
#        qs = self.get_query_set()
#        q_objects = []
#        for method in methods:
#            qs, q_object = self.process_qs(method, qs)
#            q_objects.append(q_object)
#        return qs.filter(reduce(operator.or_, q_objects))
#
#    def __getattr__(self, *args, **kwargs):
#        method = args[0]
#        if method.startswith('by_'):
#            method = method.split('_', 1)[1]
#            if method in Validators.choices:
#                def returned_funct(**kw):
#                    qs, q_object = self.process_qs(method,
#                                                    self.get_query_set(), **kw)
#                    return qs.filter(Q(q_object))
#                return returned_funct


class ContactDiscount(models.Model):
    contact = models.ForeignKey('accounts.Contact')
    discount = models.ForeignKey('Discount', related_name='used')
    already_used = models.PositiveIntegerField(default=1)


class Discount(models.Model):
    discount_types = {}

    AMOUNT_UNIT_CHOICES = [['m', 'Money'],
                           ['p', 'Percent']]

    valid = DiscountValidatorManager()
    objects = DiscountManager()

    discount_type = models.CharField(max_length=250,
                       choices=DiscountRegistr.get_choices())

    amount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    amount_unit = models.CharField(max_length=20,
                       choices=AMOUNT_UNIT_CHOICES, default='m')

    min_order_amount = models.FloatField(default=0)

    active = models.BooleanField(default=True)
    allowed_uses = models.PositiveIntegerField(default=0)
    users_used = models.ManyToManyField('accounts.Contact', blank=True,
          null=True, through='ContactDiscount', related_name='used_discounts')
    valid_users = models.ManyToManyField('accounts.Contact',
            verbose_name="Valid Users", blank=True, null=True)
    valid_products = models.ManyToManyField('products.Product',
                                            verbose_name="Valid Products",
                                            blank=True, null=True)
    valid_variations = models.ManyToManyField('products.ProductVariation',
                                            verbose_name="Valid Products",
                                            blank=True, null=True)
    start_date = models.DateField("Start Date", blank=True, null=True)
    end_date = models.DateField("End Date", blank=True, null=True)
    is_stacked = models.BooleanField(default=False)
    is_promotion = models.BooleanField(default=False)
    code = models.CharField("Discount Code", max_length=20, unique=True,
                            blank=True, null=True)

    def process_discount(self, price):
        price = price
        if self.amount_unit == 'm':
            return price - self.amount
        return price * (1 - self.amount)

    def get_discount_class(self):
        discount_class = DiscountRegistr.discounts.get(self.discount_type)
        return discount_class






