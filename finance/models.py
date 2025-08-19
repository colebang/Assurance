from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from claims.models import Claim


class Payment(models.Model):
    class Mode(models.TextChoices):
        CASH = "CASH", "Cash"
        BANK = "BANK", "Bank"
        MOBILE = "MOBILE", "Mobile"

    claim = models.ForeignKey(Claim, related_name="payments", on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_at = models.DateTimeField(default=timezone.now)
    mode = models.CharField(max_length=10, choices=Mode.choices)
    reference = models.CharField(max_length=100, blank=True, null=True, unique=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        if self.amount is None or self.amount <= 0:
            raise ValidationError({"amount": "Amount must be > 0"})

    def __str__(self) -> str:  # pragma: no cover
        return f"Payment {self.id} for {self.claim.public_code}"

    class Meta:
        ordering = ["-paid_at"]
