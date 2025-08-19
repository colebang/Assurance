from django.views.generic import ListView
from .models import AuditLog
from django_filters import FilterSet, DateFromToRangeFilter


class AuditLogFilter(FilterSet):
    performed_at = DateFromToRangeFilter()

    class Meta:
        model = AuditLog
        fields = ["action", "object_type", "performed_at"]


class AuditLogListView(ListView):
    model = AuditLog
    template_name = "audit/log_list.html"
    context_object_name = "logs"

    def get_filter(self):
        return AuditLogFilter(self.request.GET, queryset=AuditLog.objects.all())

    def get_queryset(self):
        return self.get_filter().qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filter"] = self.get_filter()
        return ctx
