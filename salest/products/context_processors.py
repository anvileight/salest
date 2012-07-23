from salest.products.models import ProductType


def categories(request):
    return {'categories': list(ProductType.objects.all()) }