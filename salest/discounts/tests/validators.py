from django_webtest import WebTest
from mock import Mock
from test_tools.utils import model_factory
from salest.products.models import Product, ProductVariation
from django.db.models import F, Q
from django.db.models.query import QuerySet
from salest.accounts.models import Contact
from salest.discounts.base import get_func_kwargs, DiscountTypeBase
from salest.discounts.models import Discount
from salest.discounts.validators import ProductValidator,\
    ProductVariationValidator, UserValidator, CodeValidator, MinOrderValidator,\
    BaseDiscountValidator, DiscountRegistr
from salest.discounts.discounts import CartCodeMinOrderDiscount
from django.core.exceptions import ValidationError


class DummyValidator(BaseDiscountValidator):
    pass


class DummyDiscount(DiscountTypeBase):
    validators = [DummyValidator]
    name = 'test'
    slug = 'test'
    target = 'cart_item'


class DummyDiscount2(DiscountTypeBase):
    validators = [DummyValidator]
    name = 'test2'
    slug = 'test2'
    target = 'cart_item'


class ValidatorsTestCase(WebTest):
    def test_registr(self):
        v1 = DummyDiscount
        DiscountRegistr.discounts = {}
        DiscountRegistr.register(v1)
        self.assertTrue('test' in DiscountRegistr.discounts)
        self.assertEqual(DiscountRegistr.discounts['test'], v1)

    def test_raises_registr(self):
        DiscountRegistr.discounts = {}
        DiscountRegistr.discounts['test'] = []
        self.assertRaises(TypeError, DiscountRegistr.register,
                          Mock())

    def test_force_registr(self):
        DiscountRegistr.discounts = {}
        DiscountRegistr.choices = {}
        DiscountRegistr.register(DummyDiscount)
        self.assertTrue('test' in DiscountRegistr.discounts)
        self.assertEqual(DiscountRegistr.discounts['test'], DummyDiscount)

    def test_unregistr(self):
        DiscountRegistr.discounts = {'test': DummyDiscount}
        DiscountRegistr.choices = {'test': 'test'}
        DiscountRegistr.unregister(DummyDiscount)
        self.assertFalse('test' in DiscountRegistr.discounts)
        self.assertFalse('test' in DiscountRegistr.choices)

    def test_get_choices(self):
        DiscountRegistr.discounts = {}
        DiscountRegistr.choices = {}
        DiscountRegistr.register(DummyDiscount)
        DiscountRegistr.register(DummyDiscount2)
        self.assertEqual(sorted(list(DiscountRegistr.get_choices())),
                         sorted([('test', 'test'), ('test2', 'test2')]))

    def test_isinstance(self):
        self.assertRaises(TypeError, DiscountRegistr.register, Mock())


class GetFuncKwargsTestCase(WebTest):

    def setUp(self):
        def test_func(first, second):
            pass
        self.test_func = test_func
        return super(GetFuncKwargsTestCase, self).setUp()

    def test_get_kwargs_pass(self):
        kwargs = {'first': 'first_val', 'second': 'second_val',
                  'third': 'third_val'}
        self.assertEqual({'first': 'first_val', 'second': 'second_val'},
                         get_func_kwargs(self.test_func, **kwargs))

    def test_get_kwargs_fail(self):
        kwargs = {'first': 'first_val', 'third': 'third_val'}
        self.assertRaises(TypeError, self.test_func,
                          **get_func_kwargs(self.test_func, **kwargs))


def create_products():
    return model_factory(Product,
                            name=['test product', 'test2 product'],
                            save=True)


def create_discounts():
    return model_factory(Discount,
                             discount_type=['test', 'test'],
                             amount=[10, 20],
                             min_order_amount=[10, 20],
                             code=[11, 10],
                             save=True)


def create_users():
    return model_factory(Contact, save=True, num=2)


def create_variations():
    products = create_products()
    return model_factory(ProductVariation,
                         product=products,
                         save=True, num=2)


class ProductValidatorClassTestCase(WebTest):


    def test_productvalidator_case1(self):
        products = create_products()
        ds = create_discounts()
        ds[0].valid_products.add(products[0])
        ds[1].valid_products.add(products[1])
        validator = ProductValidator()
        qs = Discount._base_manager.filter(validator.get_q_object(products[1]))
        self.assertEqual(set([ds[1]]), set(qs))
        qs = Discount._base_manager.filter(validator.get_q_object(products))
        self.assertEqual(set(ds), set(qs))

    def test_productvalidator_case2(self):
        products = create_products()
        ds = create_discounts()
        ds[0].valid_products.add(products[0])
        validator = ProductValidator()
        qs = Discount._base_manager.filter(validator.get_q_object(products[1]))
        self.assertEqual(set([ds[1]]), set(qs))

    def test_productvalidator_case3(self):
        products = create_products()
        ds = create_discounts()
        ds[0].valid_products.add(products[0])
        validator = ProductValidator()
        qs = Discount._base_manager.filter(validator.get_q_object(products[0]))
        self.assertEqual(set(ds), set(qs))

    def test_clean(self):
        products = create_products()
        ds = create_discounts()[0]
        ds.valid_products.add(products[0])
        validator = ProductValidator()
        self.assertRaises(ValidationError, validator.clean, ds, products[1])
        self.assertEqual(ds, validator.clean(ds, products[0]))


class ProductVariationValidatorClassTestCase(WebTest):

    def test_productvariationvalidator_case1(self):
        variations = create_variations()
        ds = create_discounts()
        ds[0].valid_variations.add(variations[0])
        ds[1].valid_variations.add(variations[1])
        validator = ProductVariationValidator()
        qs = Discount._base_manager.filter(validator.get_q_object(
                                                              variations[1]))
        self.assertEqual(set([ds[1]]), set(qs))
        qs = Discount._base_manager.filter(validator.get_q_object(variations))
        self.assertEqual(set(ds), set(qs))

    def test_productvariationvalidator_case2(self):
        variations = create_variations()
        ds = create_discounts()
        ds[0].valid_variations.add(variations[0])
        validator = ProductVariationValidator()
        qs = Discount._base_manager.filter(validator.get_q_object(variations[1]))
        self.assertEqual(set([ds[1]]), set(qs))
#
    def test_productvariationvalidator_case3(self):
        variations = create_variations()
        ds = create_discounts()
        ds[0].valid_variations.add(variations[0])
        validator = ProductVariationValidator()
        qs = Discount._base_manager.filter(validator.get_q_object(variations[0]))
        self.assertEqual(set(ds), set(qs))

    def test_clean(self):
        variations = create_variations()
        ds = create_discounts()[0]
        ds.valid_variations.add(variations[0])
        validator = ProductVariationValidator()
        self.assertRaises(ValidationError, validator.clean, ds, variations[1])
        self.assertEqual(ds, validator.clean(ds, variations[0]))


class UserValidatorClassTestCase(WebTest):

    def test_uservalidator_case1(self):
        users = create_users()
        ds = create_discounts()
        ds[0].valid_users.add(users[0])
        ds[1].valid_users.add(users[1])
        validator = UserValidator()
        qs = Discount._base_manager.filter(validator.get_q_object(users[1]))
        self.assertEqual(set([ds[1]]), set(qs))
        qs = Discount._base_manager.filter(validator.get_q_object(users))
        self.assertEqual(set(ds), set(qs))

    def test_uservalidator_case2(self):
        users = create_users()
        ds = create_discounts()
        ds[0].valid_users.add(users[0])
        validator = UserValidator()
        qs = Discount._base_manager.filter(validator.get_q_object(users[1]))
        self.assertEqual(set([ds[1]]), set(qs))

    def test_uservalidator_case3(self):
        users = create_users()
        ds = create_discounts()
        ds[0].valid_users.add(users[0])
        validator = UserValidator()
        qs = Discount._base_manager.filter(validator.get_q_object(users[0]))
        self.assertEqual(set(ds), set(qs))

    def test_clean(self):
        ds = create_discounts()[0]
        users = users = create_users()
        validator = UserValidator()
        self.assertEqual(ds, validator.clean(ds, users[0]))
        ds.valid_users.add(users[0])
        self.assertRaises(ValidationError, validator.clean, ds, users[1])
        self.assertEqual(ds, validator.clean(ds, users[0]))


class CodeValidatorClassTestCase(WebTest):

    def test_codevalidator_case1(self):
        ds = create_discounts()
        validator = CodeValidator()
        qs = Discount._base_manager.filter(validator.get_q_object(10))
        self.assertEqual(set([ds[1]]), set(qs))

    def test_codevalidator_case2(self):
        ds = create_discounts()
        validator = CodeValidator()
        qs = Discount._base_manager.filter(validator.get_q_object([10, 11]))
        self.assertEqual(set(ds), set(qs))

    def test_clean(self):
        ds = model_factory(Discount, code='123')
        validator = CodeValidator()
        self.assertRaises(ValidationError, validator.clean, ds, '456')
        self.assertEqual(ds, validator.clean(ds, '123'))


class MinOrderValidatorClassTestCase(WebTest):

    def test_min_ordervalidator_case1(self):
        ds = create_discounts()
        validator = MinOrderValidator()
        qs = Discount._base_manager.filter(validator.get_q_object(10))
        self.assertEqual(set([ds[0]]), set(qs))

    def test_min_ordervalidator_case2(self):
        ds = create_discounts()
        validator = MinOrderValidator()
        qs = Discount._base_manager.filter(validator.get_q_object(30))
        self.assertEqual(set(ds), set(qs))

    def test_clean(self):
        ds = model_factory(Discount, min_order_amount=10)
        validator = MinOrderValidator()
        self.assertRaises(ValidationError, validator.clean, ds, 5)
        self.assertEqual(ds, validator.clean(ds, 20))


class CartCodeDiscountTestCase(WebTest):
    def test_1(self):
        discount = model_factory(Discount,
                                 code=6542,
                                 min_order_amount=100.0,
                                 save=True)
        discount_type = CartCodeMinOrderDiscount()
