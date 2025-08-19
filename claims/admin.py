from django.contrib import admin

from .models import Claim, ClaimLine, Attachment


class ClaimLineInline(admin.TabularInline):
    model = ClaimLine
    extra = 0


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ("public_code", "policy", "status", "declared_at")
    list_filter = ("status", "declared_at")
    search_fields = ("public_code", "policy__insured__last_name")
    inlines = [ClaimLineInline]


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("claim", "file", "mime", "size", "uploaded_at")
