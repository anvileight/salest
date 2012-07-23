"""
Test case for product models
"""

from django_webtest import WebTest
from salest.products.models import Product, OptionName, ProductType, \
    ProductTypeOptionName, OptionValue, ProductVariation, ProductImage
from test_tools.utils import model_factory
from mock import Mock, patch


class ProductTestCase(WebTest):
    """ ProductTestCase """

    def generate_data(self):
        """
        Method for generation a data.
        """
        product_type = model_factory(ProductType, slug='ssdf', name='sdf',
                                     save=True)
        product = model_factory(Product, product_type=product_type,
                                save=True, name='product1',
                                taxable=True)
        option_value_list = []
        for i in xrange(0, 2):
            option_name = model_factory(OptionName, name='option%s' % i,
                                        save=True)
            product_type_option_name = model_factory(ProductTypeOptionName,
                           product_type=product_type,
                           option_name=option_name, save=True)
            for i in xrange(0, 5):
                product_variation = model_factory(ProductVariation,
                                                  product=product,
                                                  items_in_stock=123,
                                                  total_sold=0,
                                                  save=True,)
                option_value = model_factory(OptionValue,
                            product_type_option_name=product_type_option_name,
                            product_variation=product_variation,
                            value='option%s' % i, save=True,)
                option_value_list.append(option_value)
        return product, option_value_list

    def test_get_variations(self):
        """ Test for method get_variations in model Product """
        product = self.generate_data()[0]
        result = product.get_variations()
        self.assertTrue(result, 'Variation not found')

    def test_get_variations2(self):
        """ Test for method get_variations in model Product """
        product = self.generate_data()[0]
        option_value_list = OptionValue.objects.filter(
                product_variation__product__product_type=product.product_type)
        result = product.get_variations(option_value_list)
        result2 = product.get_variations()
        msg = "method returned different results"
        self.assertItemsEqual(result[0], result2[0], msg)
        self.assertTrue(result, 'Variation not found')

    def test_get_similar_option_value(self):
        """
        Test for method get_similar_option_value in model OptionValue
        """
        option_value_list = self.generate_data()[1]
        expected_seq = option_value_list[0].get_similar_option_value()
        actual_seq = option_value_list[0].get_similar_option_value(
                                                            option_value_list)
        msg = "method returned different results"
        self.assertItemsEqual(expected_seq, actual_seq, msg)

    def test_min_variation(self):
        product = model_factory(Product, save=True)
        self.assertEqual(product.min_variation(), None)
        variations = model_factory(ProductVariation,
                                   product = [product, product],
                                   price = [10, 20],
                                   save=True)
        self.assertEqual(product.min_variation(), variations[0])

    def test_unicode(self):
        name = 'test'
        product = model_factory(Product, name=name)
        self.assertEqual(name, str(product))


class ProductTypeTestCase(WebTest):

    def test_unicode(self):
        name = 'test'
        ptype = model_factory(ProductType, name=name)
        self.assertEqual(str(ptype), name)

    def test_get_slug(self):
        slug = 'test'
        ptype = model_factory(ProductType, slug=slug)
        self.assertEqual(ptype.get_slug(), slug)


class ProductVariationTestCase(WebTest):

    def test_clone(self):
        oname = model_factory(OptionName,
                              save=True)
        ptype = model_factory(ProductType,
                              name='test',
                              save=True)
        product_type_option_name = model_factory(ProductTypeOptionName,
                                                 product_type=ptype,
                                                 option_name=oname,
                                                 save=True)
        product = model_factory(Product, save=True)
        variation = model_factory(ProductVariation,
                                  price=10,
                                  product=product,
                                  save=True)
        value = model_factory(OptionValue,
                              value='test',
                              product_variation=variation,
                              product_type_option_name=product_type_option_name,
                              save=True)
        clone = variation.clone()
        self.assertEqual(variation.price, clone.price)
        self.assertEqual(variation.product, clone.product)
        self.assertNotEqual(variation.pk, clone.pk)

    def test_clone_fail(self):
        product = model_factory(Product, save=True)
        variation = model_factory(ProductVariation,
                                  price=10,
                                  product=product)
        self.assertRaises(ValueError, variation.clone)

    def test_unicode(self):
        product = model_factory(Product,
                                name='test',
                                save=True)
        variation = model_factory(ProductVariation,
                                  price=10,
                                  product=product,
                                  save=True)
        self.assertEqual(str(variation), 'test()')

    def test_all_images(self):
        product = model_factory(Product,
                                name='test',
                                save=True)
        img = model_factory(ProductImage,
                            img='test.jpg',
                            save=True)
        variation = model_factory(ProductVariation,
                                  price=10,
                                  product=product,
                                  save=True)
        variation.images.add(img)
        variation._images = 'test'
        self.assertEqual(variation.all_images, 'test')
        variation._images = None
        self.assertEqual(list(variation.all_images), [img])

    def test_image(self):
        product = model_factory(Product,
                                name='test',
                                save=True)
        img = model_factory(ProductImage,
                            img='test.jpg',
                            save=True)
        variation = model_factory(ProductVariation,
                                  price=10,
                                  product=product,
                                  save=True)
        self.assertEqual(variation.image, None)
        variation.images.add(img)
        variation._images = None
        self.assertEqual(variation.image, img)

    def test_get_options(self):
        oname = model_factory(OptionName,
                              name='test_option_name',
                              save=True)
        ptype = model_factory(ProductType,
                              name='test',
                              save=True)
        model_factory(ProductTypeOptionName,
                      product_type=ptype,
                      option_name=oname,
                      save=True)
        product = model_factory(Product,
                                product_type=ptype,
                                save=True)
        variation = model_factory(ProductVariation,
                                  price=10,
                                  product=product,
                                  save=True)
        self.assertEqual(variation.get_options(), {'test_option_name': '--'})

