from django.utils.importlib import import_module
from django.conf import settings
from django.conf.urls.defaults import patterns


def get_payment_forms(module_name, payment_forms=None):
    """
    Method return default or custom form if "payment_forms" is not None
    """

    module_processor = import_module('{0}.processor'.format(
                                settings.PAYMENT_MODULES[module_name]))
    forms = module_processor.DEFAULT_FORMS

    if payment_forms:
        forms = payment_forms

    return forms


def url_lookup():
    """
    Method for get all urls from payment modules
    """
    uplpatterns = None
    for module in settings.PAYMENT_MODULES:
        urls = import_module('{0}.urls'.format(
                                            settings.PAYMENT_MODULES[module]))
        if hasattr(urls, 'urlpatterns'):
            patterns = urls.urlpatterns
            if not uplpatterns:
                uplpatterns = patterns
            else:
                uplpatterns += patterns

    return uplpatterns


def get_confirm_view(module_name):
    """
    Method for get confirmation view from paymen module
    """
    module = import_module('{0}.processor'.format(
                                settings.PAYMENT_MODULES[module_name]))
    #  retutrn function instead of calling it
    return module.ConfirmPaymentView
