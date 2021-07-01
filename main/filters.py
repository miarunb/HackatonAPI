from django_filters.rest_framework import FilterSet

from main.models import Product
import django_filters

class ProductFilter(FilterSet):
    price_from = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_to = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ('category', 'brand', 'price_from', 'price_to')