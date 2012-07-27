"""
    This file consists of example models for e-comerce app based on Salest Core
    and Django.
    Every class should extend core class with basic interfaces.
"""
import datetime
import json

from django.db import models
from django.core.urlresolvers import reverse

from salest.products.interfaces import ProductInterface
import itertools
from copy import copy


SHIP_CLASS_CHOICES = (
    ('DEFAULT', 'Default'),
    ('YES', 'Shippable'),
    ('NO', 'Not Shippable')
)


class AvailableProductManager(models.Manager):

    def get_query_set(self):
        """ Add filters to all querysets in a mangeger """
        queyset = super(AvailableProductManager, self).get_query_set()
        return queyset.filter(active=True, subscription__isnull=True)


class Product(ProductInterface, models.Model):
    """ Extended Product Class """
    images = models.ManyToManyField('ProductImage', blank=True, null=True)

    name = models.CharField(max_length=255,
                            blank=False)
    short_description = models.TextField(max_length=200,
                                         default='',
                                         blank=True)
    description = models.TextField(default='',
                                   blank=True)
    active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    taxable = models.BooleanField()
    ship_class = models.CharField(choices=SHIP_CLASS_CHOICES,
                                 default="DEFAULT",
                                 max_length=10)
    product_type = models.ForeignKey('ProductType', blank=True, null=True)
    available = AvailableProductManager()
    objects = models.Manager()

    def __unicode__(self):
        """ This method defines  """
        return self.name

    _option_names = None
    @property
    def option_names(self):
        if self._option_names is None:
            self._option_names = self.product_type.option_name.all()
#            for option in :
#                self._option_names.append(option.name)
#            self._option_names.sort()
        return self._option_names

    def get_variations(self, option_value_list=None):
        """
        Method return dict option value for curent product and
        all option value for curent the product type. To get rid of the
        queries need will take option_value_list (all option value for current
        product type)
        """
        options_names = self.option_names
        variations = self.productvariation_set.all()
        values_data = {}
        for option_name in options_names:
            values_data[option_name.name] = {}
        for variation in variations:
            for val in variation.optionvalue_set.all():
                name = val.product_type_option_name.option_name.name
                value = val.value
                if value not in values_data[name]:
                    values_data[name][value] = []
                values_data[name][value].append(variation.id)
        return values_data.items()

    def min_variation(self):
        variations = list(self.productvariation_set.all())
        min_variation = sorted(variations, key=lambda obj: obj.get_price())
        if min_variation:
            min_variation = min_variation[0]
            min_variation.product = self
            return min_variation
        return None


class ProductType(models.Model):
    """ Types of product """
    slug = models.SlugField()
    name = models.CharField(max_length=250)
    option_name = models.ManyToManyField('OptionName',
                                            through='ProductTypeOptionName')

    def __unicode__(self):
        return self.name

    def get_slug(self):
        return self.slug

    def get_absolute_url(self):
        return reverse('products:category_details',args=[self.slug])

#    def get_option_name_list(self):
#        return self.option_name.all().values('name', flat=True)


class ProductVariation(models.Model):
    """ Variations (color, size) """

    images = models.ManyToManyField('ProductImage', blank=True, null=True)

    items_in_stock = models.IntegerField(default=0)
    total_sold = models.IntegerField(default=0)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField("Last modified",
                                  auto_now=True)

    product = models.ForeignKey(Product)

    price = models.DecimalField("Price", max_digits=14, decimal_places=2,
                                default='0.00')

    product_type_option_name = models.ManyToManyField(
                                                    'ProductTypeOptionName',
                                                    through='OptionValue')

    def clone(self):
        """Return an identical copy of the instance with a new ID."""
        if not self.pk:
            raise ValueError('Instance must be saved before it can be cloned.')
        duplicate = copy(self)
        # Setting pk to None tricks Django into thinking this is a new object.
        duplicate.pk = None
        duplicate.save()
        # ... but the trick loses all ManyToMany relations.
        for field in self._meta.many_to_many:
            source = getattr(self, field.attname)
            destination = getattr(duplicate, field.attname)
            for item in source.all():
                try:
                    destination.add(item)
                except:
                    pass
        for val in self.optionvalue_set.all():
            val.pk = None
            val.product_variation = duplicate
            val.save()
        return duplicate

    def get_price(self, quantity=1):
        """ Return  price """
#        price = self.prices.all()[:1]
#        if price:
#            return price[0].price
        return self.price

    def __unicode__(self):
        values = self.optionvalue_set.all()
        values = filter(lambda val: val.product_type_option_name.is_general,
                        values)
        values = map(lambda val: val.value, values)
        return '{0}({1})'.format(self.product.name, ', '.join(values))

    _images = None
    @property
    def all_images(self):
        if self._images is None:
            images = list(self.product.images.all()) + list(self.images.all())
            self._images = list(set(images))
        return self._images

    @property
    def image(self):
        imgs = self.all_images
        if len(imgs):
            return imgs[0]
        return None

    def get_options(self):
        data = {}
        values = self.optionvalue_set.all()
        values = {val.product_type_option_name.option_name_id: val.value for val in values}
        options = self.product.option_names
        for option in options:
            data[option.name] = values.get(option.id, '--')
        return data


class OptionValue(models.Model):
    """ Values of variations (through model) """
    date_value = models.DateField("Date", blank=True, null=True)
    boolean_value = models.BooleanField("Bool", default=True)
    text_value = models.TextField(max_length=200,
                                         default='',
                                         blank=True)
    product_variation = models.ForeignKey(ProductVariation)
    product_type_option_name = models.ForeignKey('ProductTypeOptionName')


    def __unicode__(self):
        return self.value
    
    class Meta:
        unique_together = (("product_variation", "product_type_option_name"),)

    
    def set_value(self, val):
#        if self.product_type_option_name.type_field == 'boolean':
#            val = bool(val)
        setattr(self, "{0}_value".format(self.product_type_option_name.type_field
                                         ), val)

        
    def get_value(self):
        return getattr(self, "{0}_value".format(self.product_type_option_name.type_field))
    value = property(get_value, set_value)

    def get_similar_option_value(self, option_value_list=None):
        """
        Method return string ProductVariation ids.
        Each all option vlaue for this poroduct type and add to list product
        variation id where we finded option name with this option name and
        option value.
        """
        if option_value_list is None:
            option_value_list = OptionValue.objects.filter(
                product_variation__product=self.get_product())
        similar_option_value = []
        for option_value in option_value_list:
            if option_value.get_option_name() == self.get_option_name() and \
                option_value.value == self.value:
                similar_option_value.append(
                                        str(option_value.product_variation.id))
        return ' '.join(similar_option_value)

    def get_product(self):
        """ Reurn product for cerent option value """
        return self.product_variation.product

    def get_option_name(self):
        """ Rerutn option name for curent option value """
        return self.product_type_option_name.option_name


class OptionName(models.Model):
    """ Names of options """
    name = models.CharField(max_length=250)

    def __unicode__(self):
        return self.name


class ProductTypeOptionName(models.Model):
    """ Product type to option name (through model) """
    COICES_TYPE = (
      ('date', 'date'),
      ('boolean', 'boolean'),
      ('text', 'text'))
    type_field = models.CharField(choices=COICES_TYPE, max_length=50)
    product_type = models.ForeignKey(ProductType)
    option_name = models.ForeignKey(OptionName)
    is_general = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s-%s" % (self.product_type.name, self.option_name.name)


class ProductHistory (models.Model):
    """ This model should store product changes history """
    product = models.ForeignKey(Product,
                                verbose_name='Product')
    diff_info = models.CharField('Information about changes',
                                 max_length=256,)
    date_added = models.DateField("Date added",
                                  auto_now_add=True)


class PriceCalculatorManager(models.Manager):
    """ Calculate prices """

    def total_items(self, cart):
        """ Return total amount of cart items products """
#        prices = self.filter(product__cartitem__cart=cart).extra(
#                    select={'each_total': 'price * shop_cartitem.quantity'}
#                )
#                .aggregate(Sum('total'))
#        print price[0].product.cartitem
        return 0  # prices
#
#    def total_prodcuts(self, cart):
#        """ Return total amount of cart items products """
#        price = self.filter(product__cartitem__cart=cart).aggregate(
#                                                                Sum('price'))
#        return price['price__sum'] or 0


class Price(models.Model):
    """ Price Class """

    product = models.ForeignKey(ProductVariation, related_name='prices')
    price = models.DecimalField("Price",
                                max_digits=14,
                                decimal_places=2
                                )
    quantity = models.IntegerField("Discount Quantity", default=1)
    expires = models.DateField("Expires", null=True, blank=True)

    objects = models.Manager()
    calculator = PriceCalculatorManager()

    def __unicode__(self):
        return "%s's price." % self.product.product.name


class ProductImage(models.Model):
    img = models.ImageField(upload_to='product_images')
    
    
    def __unicode__(self):
        try:
            return '{0}'.format(unicode(self.img.file.name))
        except:
            return 'image'

# keep this. It protect recursive imports wth listeners
from salest.products import listeners
