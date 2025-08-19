from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = "CREATE", "Create"
        UPDATE = "UPDATE", "Update"
        DELETE = "DELETE", "Delete"
        STATUS_CHANGE = "STATUS_CHANGE", "Status Change"
        IMPORT = "IMPORT", "Import"
        REPLY = "REPLY", "Reply"
        PAYMENT = "PAYMENT", "Payment"
        RECEIPT = "RECEIPT", "Receipt"

    object_type = models.CharField(max_length=100)
    object_id = models.CharField(max_length=64)
    action = models.CharField(max_length=20, choices=Action.choices)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    performed_at = models.DateTimeField(auto_now_add=True)
    diff = models.JSONField(null=True, blank=True)
    meta = models.JSONField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["object_type", "object_id"]),
            models.Index(fields=["-performed_at"]),
        ]
        ordering = ["-performed_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.action} {self.object_type} {self.object_id}"
