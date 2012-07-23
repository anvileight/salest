""" user tags module """

from django import template

register = template.Library()


def _check_discount(product, user):
    if hasattr(user, 'profile'):
        return product.has_discount() or user.profile.has_discount()
    return product.has_discount()


@register.inclusion_tag('salest_core/product_details_link.html')
def check_discount(product, user):
    """ this tag check product and user for available discounts """

    return {
            'has_discount': _check_discount(product, user),
            'product': product,
            }


@register.inclusion_tag('salest_core/available_discounts.html')
def get_discounts(product, user):
    """ this tag check product and user for available discounts """
    discounts = []
    if _check_discount(product, user):
        if hasattr(user, 'profile'):
            discounts = product.get_discounts_list() + \
                                        user.profile.get_discounts_list()
        else:
            discounts = product.get_discounts_list()
    return {
            'discounts': discounts,
            'product': product,
            }