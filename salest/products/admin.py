"""
Module for Product's admin classes
"""
from django.contrib import admin
from salest.products import models


class OptionVariationAdmin(admin.ModelAdmin):
    """ Admin class for OptionVariation """
    list_display = ('value', 'product_variation', 'product_type_option_name')


class ProductTypeAdmin(admin.ModelAdmin):
    """ Admin class for ProductType model """
    list_display = ('slug', 'name')


class OptionVariationInline(admin.TabularInline):
    """ Admin class for OptionVariation model """
    model = models.OptionValue



class ProductVariationAdmin(admin.ModelAdmin):
    """
    Admin class for ProductVariation model and create inline OptionValue
    """
    actions =['clone']
    inlines = [
        OptionVariationInline,
    ]
    
    filter_horizontal = ['images']

    def clone(self, request, queryset):
        for obj in queryset:
            obj.clone()
    clone.short_description = "Clone object"

class ProductAdmin(admin.ModelAdmin):
    filter_horizontal = ['images']

admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.ProductVariation, ProductVariationAdmin)
admin.site.register(models.Price)
admin.site.register(models.ProductHistory)
admin.site.register(models.ProductType, ProductTypeAdmin)
admin.site.register(models.OptionName)
admin.site.register(models.ProductTypeOptionName)
admin.site.register(models.ProductImage)

