"""
Vies related to Product
"""
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from salest.products.models import Product, ProductType, OptionValue,\
    OptionName


class ProductListView(ListView):
    """ Display list of available  products """
    queryset = Product.available.all()

class ProductDetailView(DetailView):
    """ Display list of available  products """
    model = Product
    def get_object(self, queryset=None):
        return self.model.objects.select_related().prefetch_related(
                  'productvariation_set', 'productvariation_set__images',
                  'productvariation_set__optionvalue_set',
                  'productvariation_set__optionvalue_set__product_type_option_name__option_name'
                  ).get(pk=self.kwargs['pk'])


class CatalogueListView(ListView):
    """ Generic view for catalogue """
    queryset = ProductType.objects.all()


class CategoryListView(ListView):
    """ Generic view for catalog items """

    def get_queryset(self):
        slug = self.kwargs['slug']
        option_value_list = OptionValue.objects.filter(
                            product_variation__product__product_type__slug=slug
                            ).select_related()
        self.queryset = option_value_list
        return self.queryset

    def get_context_data(self, **kwargs):
        slug = self.kwargs['slug']
#        kwargs['option_name_list'] = OptionName.objects.filter(
#                                       producttype__slug=slug).values_list(
#                                       'name', flat=True)
        kwargs['product_list'] = Product.objects.filter(
                    product_type__slug=slug).select_related().prefetch_related(
          'productvariation_set', 'productvariation_set__images',
          'productvariation_set__optionvalue_set__product_type_option_name',
          'productvariation_set__optionvalue_set', 'images',
          'product_type__option_name'
          )
        return ListView.get_context_data(self, **kwargs)

    def get(self, request, *args, **kwargs):
        self.template_name = "productvariation_list.html"
        response = super(ListView, self).get(self, request, *args, **kwargs)
        response.context_data['slug'] = kwargs['slug']
        return response

    def get_template_names(self):
        return ['products/productvariation_list.html']
