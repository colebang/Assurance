import pytest
from datetime import date, datetime
from django.utils import timezone
from django.urls import reverse

from catalog.models import Product, Coverage
from crm.models import Insured
from underwriting.models import Policy, PolicyCoverage
from claims.models import Claim, ClaimLine
from claims.services import approve_claim
from finance.services import receive_premium, pay_claim
from finance.models import Premium
from audit.models import AuditLog


@pytest.fixture
def setup_data():
    product = Product.objects.create(
        type=Product.Type.HEALTH,
        name="Health Basic",
        default_coverage_rate=0.5,
        waiting_days=10,
        duration_days=365,
    )
    coverage = Coverage.objects.create(
        product=product,
        name="Hosp",
        annual_limit=1000,
        coverage_rate=0.5,
    )
    insured = Insured.objects.create(
        first_name="Eva",
        last_name="Green",
        birth_date="1990-01-01",
        cnib="CNIBB1111",
    )
    policy = Policy.objects.create(
        insured=insured,
        product=product,
        start_date=date(2024,1,1),
        end_date=date(2024,12,31),
        status=Policy.Status.ACTIVE,
        premium_amount=100,
    )
    pc = PolicyCoverage.objects.get(policy=policy, coverage=coverage)
    claim = Claim.objects.create(
        policy=policy,
        incident_at=timezone.make_aware(datetime(2024,3,1)),
        invoice_amount=200,
    )
    ClaimLine.objects.create(claim=claim, policy_coverage=pc, line_invoice_amount=200)
    return policy, claim


@pytest.mark.django_db
def test_audit_logs_and_view(client, setup_data):
    policy, claim = setup_data
    assert AuditLog.objects.filter(object_type="Policy", action=AuditLog.Action.CREATE).exists()
    assert AuditLog.objects.filter(object_type="Claim", action=AuditLog.Action.CREATE).exists()
    approve_claim(claim)
    assert AuditLog.objects.filter(action=AuditLog.Action.STATUS_CHANGE, object_id=str(claim.pk)).exists()
    premium = Premium.objects.get(policy=policy)
    receive_premium(premium, amount=50, mode="CASH")
    assert AuditLog.objects.filter(action=AuditLog.Action.RECEIPT).exists()
    pay_claim(claim, amount=10, mode="CASH")
    assert AuditLog.objects.filter(action=AuditLog.Action.PAYMENT).exists()
    resp = client.get(reverse("audit:log_list"))
    assert resp.status_code == 200
