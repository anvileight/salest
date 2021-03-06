from salest.discounts.base import DiscountTypeBase
from salest.discounts.validators import CodeValidator, MinOrderValidator, \
    DiscountRegistr
from salest.discounts.models import Discount


class CartCodeMinOrderDiscount(DiscountTypeBase):
    validators = [CodeValidator, MinOrderValidator]
    slug = 'cart_minorder'
    name = 'Cart Minorder Discount'
    target = 'cart'

    def is_valid(self, code, order):
        try:
            self.discount = Discount.objects.get(code=code)
            self.errors.append('Already used.')
            return super(CartCodeMinOrderDiscount, self).is_valid(
                                                              self.discount,
                                                              code=code,
                                                              order=order)
        except Discount.DoesNotExist:
            self.errors.append('Invalid code.')
            return False


