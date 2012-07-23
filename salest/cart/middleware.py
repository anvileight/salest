from django.utils.functional import SimpleLazyObject
from salest.cart.models import Cart


def get_cart(request):
    if not hasattr(request, '_cached_cart'):
        request._cached_cart = Cart.objects.get_or_create_from_request(request)
    return request._cached_cart


class ShopingCartMiddleware(object):

    def process_request(self, request):
        assert hasattr(request, 'session'), "The ShopingCartMiddleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
        request.cart = SimpleLazyObject(lambda: get_cart(request))

