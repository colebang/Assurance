from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("products/", views.ProductListView.as_view(), name="product_list"),
    path("products/new/", views.ProductCreateView.as_view(), name="product_create"),
    path("products/<int:pk>/edit/", views.ProductUpdateView.as_view(), name="product_update"),
    path("coverages/", views.CoverageListView.as_view(), name="coverage_list"),
    path("coverages/new/", views.CoverageCreateView.as_view(), name="coverage_create"),
    path("coverages/<int:pk>/edit/", views.CoverageUpdateView.as_view(), name="coverage_update"),
]
