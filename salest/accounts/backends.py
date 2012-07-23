""" Auth backends """

from django.contrib.auth.backends import ModelBackend
from salest.accounts.models import UserConfirmation


class ConfirmationUserBackend(ModelBackend):
    """ Simple backend to authenticate trusted user """

    def authenticate(self, confirmation_code=None):
        """ Authenticate if code exists """
        try:
            user_confirmation = UserConfirmation.objects.filter(
                            key=confirmation_code).select_related('user').get()
        except UserConfirmation.DoesNotExist:
            return None
        else:
            user = user_confirmation.user
            user_confirmation.delete()
            return user
