"""
Contain abstract interfaces which declare must-have methods
"""


class ProductInterface(object):
    """ Interfacefor product object """

    def get_price(self, quantity=1):
        """ Return unit price for particular number of ordered items """
        raise NotImplementedError('Should have implemented get_price')
