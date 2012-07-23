from django import template
from salest.products.models import ProductType
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag()
def get_similar_id(all_values, current_val):
    return current_val.get_similar_option_value(all_values)


@register.filter()
def option_val_filter(all_option_value, product):
    option_value_list = []
    for option_vlue in all_option_value:
        if option_vlue.get_product() == product:
            option_value_list.append(option_vlue)
    return product.get_variations(option_value_list)


@register.filter()
def key(value, key):
    return value.get(key)


@register.filter()
def field_value(field):
    value = field.value()
    if hasattr(field.field, 'choices'):
        for val, display in field.field.choices:
            if val == value:
                return display
    return field.value()
