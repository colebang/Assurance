import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, datetime

from catalog.models import Product, Coverage
from crm.models import Insured
from underwriting.models import Policy, PolicyCoverage
from claims.models import Claim, ClaimLine
from claims.services import compute_eligibility, approve_claim
from finance.services import pay_claim


@pytest.fixture
def product_with_coverage():
    product = Product.objects.create(
        type=Product.Type.HEALTH,
        name="Health Basic",
        default_coverage_rate=0.5,
        waiting_days=10,
        duration_days=365,
    )
    coverage = Coverage.objects.create(
        product=product,
        name="Hospitalization",
        annual_limit=1000,
        coverage_rate=0.5,
    )
    return product, coverage


@pytest.fixture
def insured():
    return Insured.objects.create(
        first_name="Alice",
        last_name="Wonder",
        birth_date="1990-01-01",
        cnib="CNIB999999",
    )


@pytest.fixture
def approved_claim(product_with_coverage, insured):
    product, coverage = product_with_coverage
    policy = Policy.objects.create(
        insured=insured,
        product=product,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        status=Policy.Status.ACTIVE,
    )
    pc = PolicyCoverage.objects.get(policy=policy, coverage=coverage)
    claim = Claim.objects.create(
        policy=policy,
        incident_at=timezone.make_aware(datetime(2024, 3, 1)),
        invoice_amount=200,
    )
    ClaimLine.objects.create(claim=claim, policy_coverage=pc, line_invoice_amount=200)
    compute_eligibility(claim)
    approve_claim(claim)
    claim.refresh_from_db()
    return claim


@pytest.mark.django_db
def test_pay_claim_updates_paid_amount(approved_claim):
    claim = approved_claim
    pay_claim(claim, amount=50, mode="CASH")
    claim.refresh_from_db()
    assert claim.paid_amount == 50
    assert claim.status == Claim.Status.APPROVED


@pytest.mark.django_db
def test_partial_payments_lead_to_paid_status(approved_claim):
    claim = approved_claim
    pay_claim(claim, amount=40, mode="BANK")
    pay_claim(claim, amount=claim.reimbursable_amount - 40, mode="BANK")
    claim.refresh_from_db()
    assert claim.status == Claim.Status.PAID
    assert claim.paid_amount == claim.reimbursable_amount


@pytest.mark.django_db
def test_negative_amount_error(approved_claim):
    claim = approved_claim
    with pytest.raises(ValidationError):
        pay_claim(claim, amount=0, mode="CASH")


@pytest.mark.django_db
def test_exceeding_amount_error(approved_claim):
    claim = approved_claim
    with pytest.raises(ValidationError):
        pay_claim(claim, amount=claim.reimbursable_amount + 1, mode="CASH")


@pytest.mark.django_db
def test_pay_non_approved_claim(product_with_coverage, insured):
    product, coverage = product_with_coverage
    policy = Policy.objects.create(
        insured=insured,
        product=product,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        status=Policy.Status.ACTIVE,
    )
    pc = PolicyCoverage.objects.get(policy=policy, coverage=coverage)
    claim = Claim.objects.create(
        policy=policy,
        incident_at=timezone.make_aware(datetime(2024, 3, 1)),
        invoice_amount=100,
    )
    ClaimLine.objects.create(claim=claim, policy_coverage=pc, line_invoice_amount=100)
    compute_eligibility(claim)
    with pytest.raises(ValidationError):
        pay_claim(claim, amount=10, mode="CASH")
