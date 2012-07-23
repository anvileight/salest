"""
Accounts views
"""
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login as auth_login


class ConfirmationView(TemplateView):
    """ This View should process confirmation for new User. and logs in
        confirmed User. """

    processed_user = None

    def get_auth_user(self):
        return authenticate(confirmation_code=self.request.GET.get('key'))

    def process_user(self):
        """ Processing User Confirmation """
        user = self.get_auth_user()
        if user:
            user.is_active = True
            user.save()
        return user

    def get(self, request, *args, **kwargs):
        self.processed_user = self.process_user()
        if self.processed_user:
            auth_login(self.request, self.processed_user)
        return super(ConfirmationView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """ custom get context data """
        return {
                'params': kwargs,
                'confirmed_user': self.processed_user}
