from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from claims.models import Claim

from audit.models import AuditLog
from audit.services import audit_log

from .models import Payment, Premium, Receipt


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
            old_status = claim.status
            claim.status = Claim.Status.PAID
            claim.paid_at = timezone.now()
            claim.save(update_fields=["paid_amount", "status", "paid_at"])
            audit_log(
                AuditLog.Action.STATUS_CHANGE,
                claim,
                diff={"status": [old_status, claim.status]},
                user=created_by,
            )
        else:
            claim.save(update_fields=["paid_amount"])
        audit_log(
            AuditLog.Action.PAYMENT,
            payment,
            diff={"amount": [None, str(amount)]},
            user=created_by,
        )
    return payment


def create_policy_premium(policy) -> Premium:
    if Premium.objects.filter(policy=policy).exists():
        return Premium.objects.get(policy=policy)
    if policy.premium_amount <= 0:
        raise ValidationError("Premium amount must be > 0")
    premium = Premium.objects.create(
        policy=policy,
        amount_due=policy.premium_amount,
        due_date=policy.start_date,
    )
    audit_log(AuditLog.Action.CREATE, premium, user=None)
    return premium


def receive_premium(
    premium: Premium,
    *,
    amount,
    mode,
    reference=None,
    received_by=None,
    paid_at=None,
) -> Receipt:
    if amount <= 0:
        raise ValidationError("Amount must be > 0")
    already = premium.receipts.aggregate(total=Sum("amount"))["total"] or 0
    if already + amount > premium.amount_due:
        raise ValidationError("Amount exceeds due")
    with transaction.atomic():
        receipt = Receipt.objects.create(
            premium=premium,
            amount=amount,
            mode=mode,
            reference=reference,
            received_by=received_by,
            paid_at=paid_at or timezone.now(),
        )
        total = already + amount
        if total == premium.amount_due:
            premium.status = Premium.Status.PAID
        elif total > 0:
            premium.status = Premium.Status.PARTIALLY_PAID
        else:
            premium.status = Premium.Status.DUE
        premium.save(update_fields=["status", "updated_at"])
        audit_log(
            AuditLog.Action.RECEIPT,
            receipt,
            diff={"amount": [None, str(amount)]},
            user=received_by,
        )
    return receipt
