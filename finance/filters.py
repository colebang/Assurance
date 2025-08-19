import django_filters

from .models import Payment


class PaymentFilter(django_filters.FilterSet):
    paid_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Payment
        fields = ["mode", "claim__public_code", "paid_at"]
