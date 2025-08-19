import django_filters
from django.db.models import Q

from .models import Insured


class InsuredFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_q", label="Search")
    birth_date = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Insured
        fields = ["q", "birth_date"]

    def filter_q(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
            | Q(cnib__icontains=value)
        )
