from django.contrib import admin

from .models import Coverage, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "type",
        "default_coverage_rate",
        "waiting_days",
        "duration_days",
        "is_active",
        "created_at",
    )
    list_filter = ("type", "is_active")
    search_fields = ("name", "description")
    ordering = ("name",)


@admin.register(Coverage)
class CoverageAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "name",
        "annual_limit",
        "coverage_rate",
        "created_at",
    )
    list_filter = ("product",)
    search_fields = ("name", "product__name")
    ordering = ("product", "name")
