from django.urls import path

from .views import (
    PaymentCreateView,
    PaymentListView,
    PremiumDetailView,
    PremiumListView,
    ReceiptCreateView,
    ReceiptListView,
)

app_name = "finance"

urlpatterns = [
    path("payments/", PaymentListView.as_view(), name="payment_list"),
    path("claims/<int:pk>/pay/", PaymentCreateView.as_view(), name="payment_create"),
    path("premiums/", PremiumListView.as_view(), name="premium_list"),
    path("premiums/<int:pk>/", PremiumDetailView.as_view(), name="premium_detail"),
    path("premiums/<int:pk>/receive/", ReceiptCreateView.as_view(), name="receipt_create"),
    path("receipts/", ReceiptListView.as_view(), name="receipt_list"),
]
