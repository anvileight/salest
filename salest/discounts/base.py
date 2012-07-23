import inspect
import operator
from collections import Iterable
import re
from salest.discounts.models import Discount
from django.core.exceptions import ValidationError


def get_func_kwargs(func, **kwargs):
    args = inspect.getargspec(func)[0]
    new_kwargs = {}
    for arg in args:
        if arg != 'self' and arg in kwargs:
            new_kwargs[arg] = kwargs[arg]
    return new_kwargs


class DiscountTypeBase(object):
    validators = None
    slug = None
    name = None
    target = None

    def __init__(self, *args, **kwargs):
        self.errors = []

    def get_qs(self, qs):
        return qs

    def get_q_object(self, **kwargs):
        q_objects = []
        for validator in self.validators:
            validator = validator(self.qs)
            func_kw = get_func_kwargs(validator.get_q_object, **kwargs)
            q_object = validator.get_q_object(**func_kw)
            self.qs = validator.get_qs()
            q_objects.append(q_object)
        q_object = reduce(operator.and_, q_objects)
        return q_object

    def modify_qs(self, qs):
        for validator in self.validators:
            qs = validator.modify_qs(qs)
        return qs

    def get_discounts(self, **kwargs):
        q_object = self.get_q_object(**kwargs)
        return self.get_qs().filter(q_object)

    def apply_to(self, target):
        from salest.cart.models import CartItem, Cart
        types = {'cart_item': CartItem,
                 'cart': Cart}
        assert isinstance(target, types[self.target])
        if not target.discount.filter(is_stacked=False).exists():
            raise TypeError('Try stack non stackable discounts')
        target.discount.add(self)

    def is_valid(self, discount, **kwargs):
        for validator in self.validators:
            validator = validator()
            new_kw = get_func_kwargs(validator.clean, **kwargs)
            try:
                validator.clean(discount, **new_kw)
            except ValidationError, e:
                self.errors.append(e.messages[0])
        if self.errors:
            return False
        return True

