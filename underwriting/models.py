from decimal import Decimal
from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction, IntegrityError

from crm.models import Insured
from catalog.models import Product, Coverage


class Vehicle(models.Model):
    insured = models.ForeignKey(Insured, related_name="vehicles", on_delete=models.CASCADE)
    plate_number = models.CharField(max_length=20, unique=True)
    make = models.CharField(max_length=50, blank=True)
    model = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return self.plate_number


class Policy(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        ACTIVE = "ACTIVE", "Active"
        EXPIRED = "EXPIRED", "Expired"
        CANCELLED = "CANCELLED", "Cancelled"

    insured = models.ForeignKey(Insured, related_name="policies", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="policies", on_delete=models.PROTECT)
    policy_number = models.CharField(max_length=20, unique=True, editable=False)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    start_date = models.DateField()
    end_date = models.DateField()
    vehicle = models.ForeignKey(
        Vehicle, related_name="policies", null=True, blank=True, on_delete=models.SET_NULL
    )

    premium_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["policy_number"]),
            models.Index(fields=["status"]),
            models.Index(fields=["insured", "product"]),
            models.Index(fields=["start_date", "end_date"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return self.policy_number

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError({"end_date": "End date must be after start date."})

    def save(self, *args, **kwargs):
        if not self.policy_number:
            for _ in range(5):
                year = self.start_date.year if self.start_date else date.today().year
                prefix = f"POL{year}"
                with transaction.atomic():
                    last = (
                        Policy.objects.filter(policy_number__startswith=prefix)
                        .order_by("-policy_number")
                        .values_list("policy_number", flat=True)
                        .first()
                    )
                    seq = int(last.replace(prefix, "")) + 1 if last else 1
                    self.policy_number = f"{prefix}{seq:05d}"
                    try:
                        return super().save(*args, **kwargs)
                    except IntegrityError:
                        continue
            raise
        return super().save(*args, **kwargs)


class PolicyCoverage(models.Model):
    policy = models.ForeignKey(Policy, related_name="coverages", on_delete=models.CASCADE)
    coverage = models.ForeignKey(Coverage, on_delete=models.PROTECT)
    annual_limit = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    coverage_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("1"))],
    )
    waiting_days = models.PositiveIntegerField(default=0)
    remaining_limit = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("policy", "coverage")

    def __str__(self) -> str:  # pragma: no cover - simple repr
        return f"{self.policy.policy_number} - {self.coverage.name}"
