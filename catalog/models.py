from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models


class Product(models.Model):
    class Type(models.TextChoices):
        HEALTH = "HEALTH", "Health"
        AUTO = "AUTO", "Auto"

    type = models.CharField(max_length=10, choices=Type.choices)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    default_coverage_rate = models.DecimalField(max_digits=5, decimal_places=2)
    waiting_days = models.PositiveIntegerField(default=0)
    duration_days = models.PositiveIntegerField(default=365)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name

    def clean(self):
        super().clean()
        if not (Decimal("0") <= self.default_coverage_rate <= Decimal("1")):
            raise ValidationError({"default_coverage_rate": "Must be between 0 and 1."})
        if self.waiting_days < 0:
            raise ValidationError({"waiting_days": "Must be greater or equal to 0."})
        if self.duration_days < 1:
            raise ValidationError({"duration_days": "Must be greater or equal to 1."})


class Coverage(models.Model):
    product = models.ForeignKey(Product, related_name="coverages", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    annual_limit = models.DecimalField(max_digits=12, decimal_places=2)
    coverage_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("product", "name")

    def __str__(self) -> str:
        return f"{self.product.name} - {self.name}"

    def clean(self):
        super().clean()
        if self.annual_limit < 0:
            raise ValidationError({"annual_limit": "Must be greater or equal to 0."})
        if self.coverage_rate is not None and not (Decimal("0") <= self.coverage_rate <= Decimal("1")):
            raise ValidationError({"coverage_rate": "Must be between 0 and 1."})
