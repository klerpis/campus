import django_filters
from orders.models import Order


class OrderFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr='gte')
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr='lte')
    status = django_filters.CharFilter(field_name="status")

    class Meta:
        model = Order
        fields = ['status']
