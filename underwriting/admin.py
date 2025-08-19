from django.contrib import admin

from .models import Policy, PolicyCoverage, Vehicle


class PolicyCoverageInline(admin.TabularInline):
    model = PolicyCoverage
    extra = 0
    readonly_fields = (
        "coverage",
        "annual_limit",
        "coverage_rate",
        "waiting_days",
        "remaining_limit",
    )


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = (
        "policy_number",
        "insured",
        "product",
        "status",
        "start_date",
        "end_date",
    )
    list_filter = ("status", "product", "start_date", "end_date")
    search_fields = ("policy_number", "insured__first_name", "insured__last_name")
    ordering = ("-start_date",)
    inlines = [PolicyCoverageInline]


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("plate_number", "insured", "make", "model")
    search_fields = ("plate_number", "insured__first_name", "insured__last_name")
