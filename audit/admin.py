from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "object_type",
        "object_id",
        "action",
        "performed_by",
        "performed_at",
    )
    list_filter = ("action", "object_type")
    search_fields = ("object_type", "object_id")
