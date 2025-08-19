from django.db import IntegrityError, models, transaction
from django.db.models import Max
from django.core.exceptions import ValidationError


class Insured(models.Model):
    code = models.CharField(max_length=8, unique=True, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    cnib = models.CharField(max_length=20, unique=True, db_index=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if not self.cnib:
            raise ValidationError({"cnib": "CNIB is required"})

    def save(self, *args, **kwargs):
        if not self.code:
            while True:
                with transaction.atomic():
                    max_code = (
                        Insured.objects.aggregate(max_code=Max("code"))["max_code"]
                    )
                    next_num = 1 if not max_code else int(max_code[3:]) + 1
                    self.code = f"ASS{next_num:05d}"
                    try:
                        return super().save(*args, **kwargs)
                    except IntegrityError as e:
                        if "crm_insured.code" in str(e):
                            self.code = None
                            continue
                        raise
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
