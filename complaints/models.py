from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from crm.models import Insured
from claims.models import Claim


class Complaint(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        ANSWERED = "ANSWERED", "Answered"
        CLOSED = "CLOSED", "Closed"

    insured = models.ForeignKey(Insured, on_delete=models.PROTECT)
    claim = models.ForeignKey(Claim, on_delete=models.PROTECT, null=True, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    filed_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    answer_by = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)
    answer_text = models.TextField(null=True, blank=True)

    def clean(self):
        super().clean()
        if self.claim and self.claim.policy.insured != self.insured:
            raise ValidationError({"claim": "Claim does not belong to insured"})

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"Complaint #{self.pk}"
