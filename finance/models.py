from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from claims.models import Claim


class Premium(models.Model):
    class Status(models.TextChoices):
        DUE = "DUE", "Due"
        PARTIALLY_PAID = "PARTIALLY_PAID", "Partially paid"
        PAID = "PAID", "Paid"

    policy = models.ForeignKey(
        "underwriting.Policy", related_name="premiums", on_delete=models.PROTECT
    )
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DUE)
    currency = models.CharField(max_length=10, default="XOF")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.amount_due is None or self.amount_due <= 0:
            raise ValidationError({"amount_due": "Amount must be > 0"})

    def __str__(self) -> str:  # pragma: no cover
        return f"Premium for {self.policy.policy_number}"

    class Meta:
        ordering = ["-due_date"]


class Receipt(models.Model):
    class Mode(models.TextChoices):
        CASH = "CASH", "Cash"
        BANK = "BANK", "Bank"
        MOBILE = "MOBILE", "Mobile"

    premium = models.ForeignKey(Premium, related_name="receipts", on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_at = models.DateTimeField(default=timezone.now)
    mode = models.CharField(max_length=10, choices=Mode.choices)
    reference = models.CharField(max_length=100, blank=True, null=True, unique=True)
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        if self.amount is None or self.amount <= 0:
            raise ValidationError({"amount": "Amount must be > 0"})

    def __str__(self) -> str:  # pragma: no cover
        return f"Receipt {self.id} for {self.premium.policy.policy_number}"

    class Meta:
        ordering = ["-paid_at"]


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
