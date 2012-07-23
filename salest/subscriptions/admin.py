from django.contrib import admin
from salest.subscriptions.models import Subscription, Duration


class DurationInline(admin.TabularInline):
    model = Duration


class SubscriptionAdmin(admin.ModelAdmin):
    fields = ('name', 'short_description', 'description', 'active')
    inlines = [DurationInline]

admin.site.register(Subscription, SubscriptionAdmin)
