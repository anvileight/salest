from django.contrib import admin

from salest.core import models


admin.site.register(models.Event)
admin.site.register(models.EmailTemplate)
