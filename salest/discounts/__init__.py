from salest.discounts.validators import DiscountRegistr
from salest.discounts.discounts import CartCodeMinOrderDiscount


DiscountRegistr.register(CartCodeMinOrderDiscount)
