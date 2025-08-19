from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from claims.models import Claim

from .models import Payment


def pay_claim(
    claim: Claim,
    *,
    amount,
    mode,
    reference=None,
    created_by=None,
    paid_at=None,
) -> Payment:
    if claim.status != Claim.Status.APPROVED:
        raise ValidationError("Claim not approved")
    already_paid = claim.paid_amount
    if amount <= 0:
        raise ValidationError("Amount must be > 0")
    if already_paid + amount > claim.approved_amount:
        raise ValidationError("Amount exceeds approved total")
    with transaction.atomic():
        payment = Payment.objects.create(
            claim=claim,
            amount=amount,
            mode=mode,
            reference=reference,
            created_by=created_by,
            paid_at=paid_at or timezone.now(),
        )
        claim.paid_amount = already_paid + amount
        if claim.paid_amount >= claim.approved_amount:
            claim.status = Claim.Status.PAID
            claim.paid_at = timezone.now()
            claim.save(update_fields=["paid_amount", "status", "paid_at"])
        else:
            claim.save(update_fields=["paid_amount"])
    return payment
