"""
    This module consists of Order classes and functionality
"""


class Order(object):
    pass
#    def __init__(self, user):
#        info = [OderItem.create(prod) for item in cart]
#        super(Order, self).__init__(info)
#        pass


class OrderItem(object):
    cart_item = None

    @staticmethod
    def create(cart_item):
        return OrderItem(cart_item)

#    def __init__(self, cart_item):
#        self.cart_item = cart_item

    def get_quantity(self):
        pass
