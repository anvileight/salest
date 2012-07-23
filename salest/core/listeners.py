""" This file should store signals listeners function. """

#from django.dispatch import receiver
#
#from core.signals import page_view, product_added_to_cart, \
#                                product_removed_from_cart


def record_event(data):
    """ Basic function that should record Event information from signals. """
    from core.models import Event

#    Event.objects.using('events_storage').create(**data)
    Event.objects.create(**data)

#@receiver(page_view, dispatch_uid="page_view")
#def page_view_listener(sender, signal_info, **kwargs):
#    """ This function should listen page view signal """
#    record_event({'signal_type': 'PV',
#                  'signal_info': signal_info,})
#
#@receiver(product_added_to_cart)
#def event_recorder(sender, product, **kwargs):
#    """ This function should listen product added to cart signal """
#    record_event({'signal_type': 'product added to cart',
#                  'signal_info': product,})
#
#@receiver(product_removed_from_cart,
#                            dispatch_uid="product_removed_from_cart_listener")
#def product_removed_from_cart_listener(sender, signal_info, **kwargs):
#    """ This function should listen product removed from cart signal """
#    record_event({'signal_type': 'PRFC',
#                  'signal_info': signal_info,})
