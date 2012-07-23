from django.contrib import admin
from salest.discounts import models

admin.site.register(models.Discount)
admin.site.register(models.ContactDiscount)
