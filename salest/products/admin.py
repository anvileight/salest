"""
Module for Product's admin classes
"""
from django.contrib import admin
from salest.products import models
from salest.products.forms import ProductVariationForm, OptionValueForm
from salest.products.models import ProductVariation
from django.forms.models import inlineformset_factory, modelformset_factory,\
    modelform_factory
from django import forms


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
    form = ProductVariationForm
    actions =['clone']
    filter_horizontal = ['images']

    def clone(self, request, queryset):
        for obj in queryset:
            obj.clone()
    clone.short_description = "Clone object"
    

def product_variation_form_factory(parent, fields):
    return type(parent.__name__ + 'Tmp', (parent,), fields)

class ProductVariationInline(admin.TabularInline):
    extra = 0
    model = ProductVariation
    
    def __init__(self, parent_model, admin_site):
        admin.TabularInline.__init__(self, parent_model, admin_site)
        self.form


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductVariationInline]
    search_fields = ('name', )
    list_filter = ('product_type',)
    filter_horizontal = ['images']
    
    def change_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, object_id)
        product_type_option_names = obj.product_type.producttypeoptionname_set.all()
        form_fields = OptionValueForm().fields
        fields = {}
        fields['product_type_option_name'] = {}
        for product_type_option_name in product_type_option_names:
            name = product_type_option_name.option_name.name
            form_field = form_fields[product_type_option_name.type_field+'_value']
            form_field.label = name
            fields['product_type_option_name'][name] = product_type_option_name.id
            fields['custom_' + name] = form_field
        self.inlines[0].form = product_variation_form_factory(ProductVariationForm, fields)
        return admin.ModelAdmin.change_view(self, request, object_id, extra_context=extra_context)

admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.ProductVariation, ProductVariationAdmin)
admin.site.register(models.Price)
admin.site.register(models.ProductHistory)
admin.site.register(models.ProductType, ProductTypeAdmin)
admin.site.register(models.OptionName)
admin.site.register(models.ProductTypeOptionName)
admin.site.register(models.ProductImage)
admin.site.register(models.OptionValue)

