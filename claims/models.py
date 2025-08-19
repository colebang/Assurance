from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone
from datetime import timedelta

from underwriting.models import Policy, PolicyCoverage


class Claim(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "SUBMITTED", "Submitted"
        APPROVED = "APPROVED", "Approved"
        PAID = "PAID", "Paid"
        REJECTED = "REJECTED", "Rejected"

    policy = models.ForeignKey(Policy, related_name="claims", on_delete=models.CASCADE)
    public_code = models.CharField(max_length=50, unique=True, editable=False)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SUBMITTED)
    incident_at = models.DateTimeField()
    declared_at = models.DateTimeField(auto_now_add=True)
    invoice_amount = models.DecimalField(max_digits=12, decimal_places=2)
    reimbursable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    approved_at = models.DateTimeField(null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    paid_at = models.DateTimeField(null=True, blank=True)
    reject_reason = models.TextField(blank=True)

    def clean(self):
        super().clean()
        if self.policy.status != Policy.Status.ACTIVE:
            raise ValidationError({"policy": "Policy must be ACTIVE"})
        if self.incident_at.date() < self.policy.start_date or self.incident_at.date() > self.policy.end_date:
            raise ValidationError({"incident_at": "Incident outside policy period"})
        min_wait = self.policy.coverages.aggregate(models.Min("waiting_days"))["waiting_days__min"] or 0
        if self.incident_at.date() < self.policy.start_date + timedelta(days=min_wait):
            raise ValidationError({"incident_at": "Incident within waiting period"})

    def save(self, *args, **kwargs):
        if not self.public_code:
            from .services import generate_public_code

            self.public_code = generate_public_code(self)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return self.public_code

    @property
    def approved_amount(self):  # pragma: no cover - simple alias
        return self.reimbursable_amount

    class Meta:
        permissions = [
            ("approve_claim", "Peut approuver un sinistre"),
            ("reject_claim", "Peut rejeter un sinistre"),
            ("mark_paid_claim", "Peut marquer payé"),
        ]


class ClaimLine(models.Model):
    claim = models.ForeignKey(Claim, related_name="lines", on_delete=models.CASCADE)
    policy_coverage = models.ForeignKey(PolicyCoverage, on_delete=models.PROTECT)
    line_invoice_amount = models.DecimalField(max_digits=12, decimal_places=2)
    line_eligible_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    line_approved_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.claim.public_code} - {self.policy_coverage.coverage.name}"


class Attachment(models.Model):
    claim = models.ForeignKey(Claim, related_name="attachments", on_delete=models.CASCADE)
    file = models.FileField(upload_to="claims/attachments/", validators=[
        FileExtensionValidator(["jpg", "jpeg", "png", "pdf"])
    ])
    mime = models.CharField(max_length=100, blank=True)
    size = models.PositiveIntegerField(null=True, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        if self.file and not self.size:
            self.size = self.file.size
        if self.file and not self.mime:
            self.mime = getattr(self.file, "content_type", "")
        max_size = 5 * 1024 * 1024
        if self.size and self.size > max_size:
            raise ValidationError("File too large")
        allowed = {"image/jpeg", "image/png", "application/pdf"}
        if self.mime and self.mime not in allowed:
            raise ValidationError("Invalid file type")

    def __str__(self) -> str:  # pragma: no cover
        return self.file.name
