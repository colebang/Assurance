import django_filters

from .models import Policy
from catalog.models import Product


class PolicyFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=Policy.Status.choices)
    product = django_filters.ModelChoiceFilter(queryset=Product.objects.all())
    start_date = django_filters.DateFromToRangeFilter()
    end_date = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Policy
        fields = ["status", "product", "start_date", "end_date"]
