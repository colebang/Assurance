from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView, View

from accounts.permissions import RoleRequiredMixin

from . import services


class DGDashboardView(RoleRequiredMixin, TemplateView):
    required_roles = ("dg",)
    template_name = "dashboard/dg.html"


class DGCountersAPI(RoleRequiredMixin, View):
    required_roles = ("dg",)
    def get(self, request, *args, **kwargs):
        return JsonResponse(services.counters())


class DGSeriesAPI(RoleRequiredMixin, View):
    required_roles = ("dg",)
    def get(self, request, *args, **kwargs):
        metric = request.GET.get("metric")
        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")
        period = request.GET.get("period", "day")
        data = services.series(metric, date_from, date_to, period)
        return JsonResponse(data)


class DGExportCSV(RoleRequiredMixin, View):
    required_roles = ("dg",)
    def get(self, request, *args, **kwargs):
        metric = request.GET.get("metric")
        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")
        period = request.GET.get("period", "day")
        data = services.series(metric, date_from, date_to, period)
        import csv
        from io import StringIO

        sio = StringIO()
        writer = csv.writer(sio)
        writer.writerow(["label"] + data.get("labels", []))
        for ds in data.get("datasets", []):
            writer.writerow([ds.get("label")] + ds.get("data", []))
        response = HttpResponse(sio.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=export.csv"
        return response
