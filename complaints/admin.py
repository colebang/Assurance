from django.contrib import admin

from .models import Complaint


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("insured", "claim", "status", "filed_at")
    list_filter = ("status", "filed_at")
    search_fields = (
        "insured__first_name",
        "insured__last_name",
        "claim__public_code",
    )
