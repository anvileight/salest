"""
    This module should consists of custom signals for management app.
"""

from django.dispatch import Signal
#necessary signals
page_view = Signal(providing_args=['signal_info'])
product_added_to_cart = Signal(providing_args=['product'])
product_removed_from_cart = Signal(providing_args=['product'])

#product_ended_in_stock = Signal(providing_args=['signal_info'])
#product_almost_ended_in_stock = Signal(providing_args=['signal_info'])
#
#invited_user_came = Signal(providing_args=['signal_info'])
#invited_user_signup = Signal(providing_args=['signal_info'])
#
#discount_asked = Signal(providing_args=['signal_info'])
#
#
#
##TODO: This list of signals should be checked
#
##IN ORDER
##payment_system_used = Signal(providing_args=['sender', ])
##shipping_system_used = Signal(providing_args=['sender', ])
##cart_purchased = Signal(providing_args=['sender', ])
##discount_used = Signal(providing_args=['sender', ])
#
#
#user_invited = Signal(providing_args=['signal_info', ])
#discount_fully_used = Signal(providing_args=['signal_info', ])
