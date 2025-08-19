import django_filters

from .models import Claim


class ClaimFilter(django_filters.FilterSet):
    public_code = django_filters.CharFilter(lookup_expr="icontains")
    declared_at = django_filters.DateFromToRangeFilter()
    insured_last_name = django_filters.CharFilter(
        field_name="policy__insured__last_name", lookup_expr="icontains"
    )

    class Meta:
        model = Claim
        fields = ["public_code", "status", "insured_last_name", "declared_at"]
