"""
Contain abstract interfaces which declare must-have methods
"""


class OrderInterface(object):
    """ Interface for order object """

    def get_order_price(self):
        """
        Return total items price including per item discounts but excluding
        everything that applied to the resulted ammount like taxes, cart and
        user discoutns
        """
        raise NotImplementedError()

    def get_full_order_price(self):
        """
        Return total price including taxes, shipping, discount prices
        """
        raise NotImplementedError()

    @property
    def items(self):
        """ Return all the order items """
        raise NotImplementedError()

    def confirm(self, **kwargs):
        """
        Send order to payment module and return complite order
        """
        raise NotImplementedError()

    def get_total_quantity(self):
        """
        Return total quantity of items in order
        """
        raise NotImplementedError()
