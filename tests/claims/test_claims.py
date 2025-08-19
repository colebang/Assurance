import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from datetime import date, datetime

from catalog.models import Product, Coverage
from crm.models import Insured
from underwriting.models import Policy, PolicyCoverage
from claims.models import Claim, ClaimLine, Attachment
from claims.services import compute_eligibility, approve_claim
from claims.forms import AttachmentFormSet


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
        cnib="CNIB7654321",
    )


@pytest.fixture
def policy(product_with_coverage, insured):
    product, coverage = product_with_coverage
    policy = Policy.objects.create(
        insured=insured,
        product=product,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        status=Policy.Status.ACTIVE,
    )
    pc = PolicyCoverage.objects.get(policy=policy, coverage=coverage)
    return policy, pc


@pytest.mark.django_db
def test_claim_public_code(policy):
    policy_obj, pc = policy
    claim = Claim.objects.create(
        policy=policy_obj,
        incident_at=timezone.make_aware(datetime(2024, 1, 20)),
        invoice_amount=100,
    )
    assert claim.public_code.startswith(f"SINS-{policy_obj.insured.code}-")


@pytest.mark.django_db
def test_waiting_period_and_policy_status(policy):
    policy_obj, pc = policy
    # incident before waiting period
    claim = Claim(
        policy=policy_obj,
        incident_at=timezone.make_aware(datetime(2024, 1, 5)),
        invoice_amount=50,
    )
    with pytest.raises(ValidationError):
        claim.full_clean()
    # policy not active
    policy_obj.status = Policy.Status.EXPIRED
    policy_obj.save()
    claim2 = Claim(
        policy=policy_obj,
        incident_at=timezone.make_aware(datetime(2024, 2, 1)),
        invoice_amount=50,
    )
    with pytest.raises(ValidationError):
        claim2.full_clean()


@pytest.mark.django_db
def test_compute_eligibility(policy):
    policy_obj, pc = policy
    claim = Claim.objects.create(
        policy=policy_obj,
        incident_at=timezone.make_aware(datetime(2024, 3, 1)),
        invoice_amount=300,
    )
    ClaimLine.objects.create(claim=claim, policy_coverage=pc, line_invoice_amount=200)
    ClaimLine.objects.create(claim=claim, policy_coverage=pc, line_invoice_amount=100)
    compute_eligibility(claim)
    assert claim.reimbursable_amount == pytest.approx(150)


@pytest.mark.django_db
def test_approve_claim_decrements_remaining(policy):
    policy_obj, pc = policy
    claim = Claim.objects.create(
        policy=policy_obj,
        incident_at=timezone.make_aware(datetime(2024, 3, 1)),
        invoice_amount=200,
    )
    ClaimLine.objects.create(claim=claim, policy_coverage=pc, line_invoice_amount=200)
    compute_eligibility(claim)
    remaining_before = pc.remaining_limit
    approve_claim(claim)
    pc.refresh_from_db()
    assert pc.remaining_limit == remaining_before - claim.reimbursable_amount


@pytest.mark.django_db
def test_attachment_constraints(policy):
    policy_obj, pc = policy
    claim = Claim.objects.create(
        policy=policy_obj,
        incident_at=timezone.make_aware(datetime(2024, 3, 1)),
        invoice_amount=100,
    )
    big_content = b"x" * (6 * 1024 * 1024)
    big_file = SimpleUploadedFile("big.jpg", big_content, content_type="image/jpeg")
    att = Attachment(claim=claim, file=big_file, mime="image/jpeg", size=len(big_content))
    with pytest.raises(ValidationError):
        att.full_clean()
    data = {
        'attachment_set-TOTAL_FORMS': '6',
        'attachment_set-INITIAL_FORMS': '0',
        'attachment_set-MIN_NUM_FORMS': '0',
        'attachment_set-MAX_NUM_FORMS': '1000',
    }
    files = {}
    for i in range(6):
        data[f'attachment_set-{i}-file'] = ''
        files[f'attachment_set-{i}-file'] = SimpleUploadedFile(f'f{i}.jpg', b'a', content_type='image/jpeg')
    formset = AttachmentFormSet(data, files, instance=claim, prefix='attachment_set')
    assert not formset.is_valid()


@pytest.mark.django_db
def test_claim_list_view(client, policy):
    policy_obj, pc = policy
    Claim.objects.create(
        policy=policy_obj,
        incident_at=timezone.make_aware(datetime(2024, 3, 1)),
        invoice_amount=50,
    )
    url = reverse("claims:claim_list")
    resp = client.get(url, {"status": Claim.Status.SUBMITTED})
    assert resp.status_code == 200
