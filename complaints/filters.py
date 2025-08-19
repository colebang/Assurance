import django_filters
from django.db.models import Q

from .models import Complaint


class ComplaintFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_q", label="Search")
    filed_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Complaint
        fields = ["status"]

    def filter_q(self, queryset, name, value):
        return queryset.filter(
            Q(insured__last_name__icontains=value)
            | Q(claim__public_code__icontains=value)
        )
