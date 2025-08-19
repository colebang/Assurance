from django.urls import path

from .views import PaymentCreateView, PaymentListView

app_name = "finance"

urlpatterns = [
    path("payments/", PaymentListView.as_view(), name="payment_list"),
    path("claims/<int:pk>/pay/", PaymentCreateView.as_view(), name="payment_create"),
]
