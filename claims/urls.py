from django.urls import path

from .views import (
    ClaimListView,
    ClaimCreateView,
    ClaimDetailView,
    ClaimApproveView,
    ClaimRejectView,
)

app_name = "claims"

urlpatterns = [
    path("", ClaimListView.as_view(), name="claim_list"),
    path("new/", ClaimCreateView.as_view(), name="claim_create"),
    path("<int:pk>/", ClaimDetailView.as_view(), name="claim_detail"),
    path("<int:pk>/approve/", ClaimApproveView.as_view(), name="claim_approve"),
    path("<int:pk>/reject/", ClaimRejectView.as_view(), name="claim_reject"),
]
