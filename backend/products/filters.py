from django_filters import rest_framework as filters
from .models import Product

class ProductFilter(filters.FilterSet):
    """商品过滤器"""
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    category = filters.NumberFilter(field_name="category__id")
    is_featured = filters.BooleanFilter(field_name="is_featured")
    is_active = filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = Product
        fields = ['category', 'is_featured', 'is_active']