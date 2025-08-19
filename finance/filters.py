import django_filters

from .models import Payment, Premium, Receipt


class PaymentFilter(django_filters.FilterSet):
    paid_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Payment
        fields = ["mode", "claim__public_code", "paid_at"]


class PremiumFilter(django_filters.FilterSet):
    due_date = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Premium
        fields = ["status", "policy__policy_number", "due_date"]


class ReceiptFilter(django_filters.FilterSet):
    paid_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Receipt
        fields = ["mode", "premium__policy__policy_number", "paid_at"]
