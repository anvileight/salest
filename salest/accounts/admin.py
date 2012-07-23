""" """

from django.contrib import admin

from salest.accounts import models

admin.site.register(models.Wishlist)
admin.site.register(models.Invitation)
admin.site.register(models.Contact)
admin.site.register(models.UserConfirmation)
admin.site.register(models.Address)
