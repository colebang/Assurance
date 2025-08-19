from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("claim", "amount", "mode", "paid_at", "reference", "created_by")
    list_filter = ("mode", "paid_at")
    search_fields = ("reference", "claim__public_code")
