import django_filters

from .models import Coverage, Product


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Product
        fields = ["type", "name", "is_active"]


class CoverageFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Coverage
        fields = ["product", "name"]
