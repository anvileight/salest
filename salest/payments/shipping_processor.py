from django.conf import settings
from django.utils.importlib import import_module


def get_shipping_methods(cart=None):
    choices = {}
    if cart:
        for module in settings.SHIPPING_MODULES:
            module_obj = import_module('{0}.processor'.format(
                                            settings.SHIPPING_MODULES[module]))
            choices.update({module: {'name': module_obj.VERBOSE_NAME,
                                 'price': module_obj.get_shipping_cost(cart)}})
    return choices
