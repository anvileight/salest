from django import template

register = template.Library()


@register.inclusion_tag('cart_face.html')
def cart_face(cart):
    return {'cart': cart}
