from django.urls import path

from .views import (
    InsuredCreateView,
    InsuredDetailView,
    InsuredListView,
    InsuredUpdateView,
)

app_name = "crm"

urlpatterns = [
    path("", InsuredListView.as_view(), name="insured_list"),
    path("new/", InsuredCreateView.as_view(), name="insured_create"),
    path("<int:pk>/", InsuredDetailView.as_view(), name="insured_detail"),
    path("<int:pk>/edit/", InsuredUpdateView.as_view(), name="insured_update"),
]
