"""
Contain abstract interfaces which declare must-have methods
"""


class CartInterface(object):
    """ Interface for cart object """

    def get_items_price(self):
        """
        Return total items price including per item discounts but excluding
        everything that applied to the resulted ammount like taxes, cart and
        user discoutns
        """
        raise NotImplementedError()

    @property
    def items(self):
        """ Return all the cart items """
        raise NotImplementedError()

    @items.setter
    def items(self, value):
        """ Set the cart items """
        raise NotImplementedError()

    def add_product(self, product, quantity=1):
        """ Add a cart item into cart or create the cart and add item """
        raise NotImplementedError()

    def checkout(self, **kwargs):
        """
        Create and return prepared order. kwargs would be passed to order
        create method
        """
        raise NotImplementedError()
