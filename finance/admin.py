from django.contrib import admin


from .models import Payment, Premium, Receipt


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("claim", "amount", "mode", "paid_at", "reference", "created_by")
    list_filter = ("mode", "paid_at")
    search_fields = ("reference", "claim__public_code")



@admin.register(Premium)
class PremiumAdmin(admin.ModelAdmin):
    list_display = ("policy", "amount_due", "status", "due_date")
    list_filter = ("status", "due_date")
    search_fields = ("policy__policy_number",)


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ("premium", "amount", "mode", "paid_at", "reference", "received_by")
    list_filter = ("mode", "paid_at")
    search_fields = ("reference", "premium__policy__policy_number")

