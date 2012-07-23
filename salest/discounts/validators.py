from collections import Iterable
from django.db.models import Q
import operator
import re
from django.core.exceptions import ValidationError


class DiscountRegistr(object):
    discounts = {}
    choices = {}

    @classmethod
    def register(cls, discount_type, force=False):
        required_attrs = ['validators', 'slug', 'name', 'slug']
        for attr in required_attrs:
            if not hasattr(discount_type, attr):
                raise TypeError("{0} discount type must have {1} attribute"\
                                ".".format(discount_type, attr))
        validators = discount_type.validators
        if not isinstance(validators, Iterable):
            validators = [validators]
        for validator in validators:
            if not isinstance(validator, type) or not issubclass(validator,
                                                 BaseDiscountValidator):
                raise TypeError('{0} must be subclass of {1}'.format(
                                                              validator,
                                                  BaseDiscountValidator))
        slug = discount_type.slug
        if not re.match(r'^[a-z]+\w+$', slug):
            raise TypeError('Slug "{0}" should match '
                             '"^[a-z]+\w+$"'.format(slug))
        if slug in cls.discounts:
            raise TypeError('Discount with slug "{0}" already'
                            ' registr.'.format(slug))
        if discount_type.target not in ['cart_item', 'cart']:
            raise TypeError("{0} attribute 'target' must be 'cart'"\
                            " or 'cart_item'".format(discount_type))
        cls.discounts[slug] = discount_type
        cls.choices[slug] = str(discount_type.name)

    @classmethod
    def unregister(cls, discount_type):
        if discount_type.slug in cls.discounts:
            del cls.discounts[discount_type.slug]
            del cls.choices[discount_type.slug]

    @classmethod
    def get_choices(cls):
        for choice in cls.choices.items():
            yield choice


class BaseDiscountValidator(object):
    def get_q_object(self):
        raise NotImplementedError('Must return "Q" object.')

    def modify_qs(self, qs):
        return qs

    def clean(self, discount, **kwargs):
        raise NotImplementedError


class UserValidator(BaseDiscountValidator):

    def get_q_object(self, user):
        if isinstance(user, Iterable):
            q = Q(valid_users__in=user)
        else:
            q = Q(valid_users=user)
        return operator.or_(q, Q(valid_users__isnull=True))

    def clean(self, discount, user):
        valid_users = discount.valid_users.all()
        if valid_users and user not in valid_users:
            raise ValidationError('Invalid user')
        return discount


class ProductValidator(BaseDiscountValidator):

    def get_q_object(self, product):
        if isinstance(product, Iterable):
            q = Q(valid_products__in=product)
        else:
            q = Q(valid_products=product)
        return operator.or_(q, Q(valid_products__isnull=True))

    def clean(self, discount, product):
        valid_products = discount.valid_products.all()
        if valid_products and product not in valid_products:
            raise ValidationError('Invalid product.')
        return discount


class ProductVariationValidator(BaseDiscountValidator):

    def get_q_object(self, variation):
        if isinstance(variation, Iterable):
            q = Q(valid_variations__in=variation)
        else:
            q = Q(valid_variations=variation)
        return operator.or_(q, Q(valid_variations__isnull=True))

    def clean(self, discount, variation):
        valid_variations = discount.valid_variations.all()
        if valid_variations and variation not in valid_variations:
            raise ValidationError('Invalid product variation.')
        return discount


class CodeValidator(BaseDiscountValidator):

    def get_q_object(self, code):
        if isinstance(code, Iterable):
            return Q(code__in=code)
        else:
            return Q(code=code)

    def clean(self, discount, code):
        if discount.code != str(code):
            raise ValidationError('Invalid code.')
        return discount


class MinOrderValidator(BaseDiscountValidator):

    def get_q_object(self, order):
        return Q(min_order_amount__lte=order)

    def clean(self, discount, order):
        if discount.min_order_amount > order:
            raise ValidationError('Min order.')
        return discount



