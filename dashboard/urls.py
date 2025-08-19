from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("dg/", views.DGDashboardView.as_view(), name="dg_dashboard"),
    path("dg/api/counters/", views.DGCountersAPI.as_view(), name="dg_counters"),
    path("dg/api/series/", views.DGSeriesAPI.as_view(), name="dg_series"),
    path("dg/api/export.csv", views.DGExportCSV.as_view(), name="dg_export"),
]
