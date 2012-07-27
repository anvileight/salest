from django import forms
from salest.products import models
import datetime
from django.forms.models import modelform_factory
from salest.products.models import OptionValue
from django.forms.formsets import formset_factory
from django.contrib.admin import widgets 


class OptionValueForm(forms.ModelForm):
    date_value = forms.DateField(widget=widgets.AdminDateWidget())
    class Meta:
        model = OptionValue


class ProductVariationForm(forms.ModelForm):
    
    def get_custom_fields(self):
        fields = []
        for field_name in self.fields.keys():
            if field_name.startswith('custom_'):
                fields.append(field_name)
        return fields
    
    def __init__(self, *args, **kwargs):
        super(ProductVariationForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        self._instance = instance
        if instance:
            values = instance.optionvalue_set.all().select_related()
            values = {'custom_' + val.product_type_option_name.option_name.name:\
                                    val.value for val in values}
            for field in self.get_custom_fields():
                self.fields[field].initial = values.get(field)

    def save(self, commit=True):
        instance = super(ProductVariationForm, self).save(commit=commit)
        if instance.pk is None:
            instance.save()
        for field in self.get_custom_fields():
            name = field.split('_', 1)[-1]
            id = self.product_type_option_name[name]
            val = instance.optionvalue_set.get_or_create(
                       product_type_option_name_id=id)[0]
            val.value = self.cleaned_data.get(field)
            val.save()
        return instance

    class Meta:
        model = models.ProductVariation