from __future__ import annotations
from django.db import transaction
from django.utils import timezone

from audit.models import AuditLog
from audit.services import audit_log

from .models import Claim


def generate_public_code(claim: Claim) -> str:
    insured_code = claim.policy.insured.code
    ts = timezone.localtime().strftime("%Y%m%d%H%M%S")
    return f"SINS-{insured_code}-{ts}"


def compute_eligibility(claim: Claim) -> None:
    total = 0
    for line in claim.lines.all():
        coverage_rate = line.policy_coverage.coverage_rate or 0
        eligible = min(
            line.line_invoice_amount * coverage_rate,
            line.policy_coverage.remaining_limit,
        )
        line.line_eligible_amount = eligible
        line.save(update_fields=["line_eligible_amount"])
        total += eligible
    claim.reimbursable_amount = total
    claim.save(update_fields=["reimbursable_amount"])


def approve_claim(claim: Claim) -> Claim:
    with transaction.atomic():
        compute_eligibility(claim)
        for line in claim.lines.select_for_update():
            amount = line.line_approved_amount or line.line_eligible_amount
            pc = line.policy_coverage
            pc.remaining_limit -= amount
            pc.save(update_fields=["remaining_limit"])
        old_status = claim.status
        claim.status = Claim.Status.APPROVED
        claim.approved_at = timezone.now()
        claim.save(update_fields=["status", "approved_at"])
        audit_log(
            AuditLog.Action.STATUS_CHANGE,
            claim,
            diff={"status": [old_status, claim.status]},
        )
    return claim
