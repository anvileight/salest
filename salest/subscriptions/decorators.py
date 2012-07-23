from django.http import HttpResponseRedirect
from django.conf import settings


def for_member_only(subscription_type=None):
    """
    Decorator that set view for members only or for group of members
    """
    def new(function):
        def is_member(request):
            try:
                subscriptions = request.user.membeship.all()
            except AttributeError:
                return HttpResponseRedirect(settings.NOT_MEMBER_URL)
            else:
                if len(subscriptions) and subscription_type is None:
                    return function(request)
                if subscription_type and subscription_type in\
                        [subscription.type for subscription in subscriptions]:
                    return function(request)

                return HttpResponseRedirect(settings.NOT_MEMBER_URL)

        return is_member

    return new
