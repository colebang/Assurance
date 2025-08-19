from django.urls import path

from .views import (
    PolicyCreateView,
    PolicyDetailView,
    PolicyListView,
    PolicyUpdateView,
    VehicleCreateView,
    VehicleListView,
    VehicleUpdateView,
)

app_name = "underwriting"

urlpatterns = [
    path("policies/", PolicyListView.as_view(), name="policy_list"),
    path("policies/new/", PolicyCreateView.as_view(), name="policy_create"),
    path("policies/<int:pk>/edit/", PolicyUpdateView.as_view(), name="policy_update"),
    path("policies/<int:pk>/detail/", PolicyDetailView.as_view(), name="policy_detail"),
    path("vehicles/", VehicleListView.as_view(), name="vehicle_list"),
    path("vehicles/new/", VehicleCreateView.as_view(), name="vehicle_create"),
    path("vehicles/<int:pk>/edit/", VehicleUpdateView.as_view(), name="vehicle_update"),
]
