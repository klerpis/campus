import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    vendor = django_filters.NumberFilter(
        field_name='store__vendor')  # supports ?vendor=2
    store = django_filters.NumberFilter(
        field_name='store')            # supports ?store=5
    category = django_filters.CharFilter(
        field_name='category__category_name', lookup_expr='iexact')

    class Meta:
        model = Product
        fields = ['vendor', 'store', 'category']
