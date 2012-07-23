from salest.discounts.validators import DiscountRegistr
from salest.discounts.discounts import CartCodeMinOrderDiscount,\
    CartCodeMinOrderInfinityDiscount


DiscountRegistr.register(CartCodeMinOrderDiscount)
DiscountRegistr.register(CartCodeMinOrderInfinityDiscount)
