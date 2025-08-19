import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from datetime import date, datetime, timedelta

from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.urls import reverse
from catalog.models import Product, Coverage
from crm.models import Insured
from underwriting.models import Policy, PolicyCoverage
from claims.models import Claim, ClaimLine
from claims.services import compute_eligibility
from complaints.models import Complaint


@pytest.fixture
def product_with_coverage():
    product = Product.objects.create(
        type=Product.Type.HEALTH,
        name="Health Basic",
        default_coverage_rate=0.5,
        waiting_days=0,
        duration_days=365,
    )
    coverage = Coverage.objects.create(
        product=product,
        name="Hosp",
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
        cnib="CNIB123456",
    )


@pytest.fixture
def prepared_claim(product_with_coverage, insured):
    product, coverage = product_with_coverage
    policy = Policy.objects.create(
        insured=insured,
        product=product,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=365),
        status=Policy.Status.ACTIVE,
    )
    pc = PolicyCoverage.objects.get(policy=policy, coverage=coverage)
    claim = Claim.objects.create(
        policy=policy,
        incident_at=timezone.now(),
        invoice_amount=100,
    )
    ClaimLine.objects.create(claim=claim, policy_coverage=pc, line_invoice_amount=100)
    compute_eligibility(claim)
    return claim


@pytest.mark.django_db
def test_complaint_creation_and_mismatch(prepared_claim):
    claim = prepared_claim
    insured = claim.policy.insured
    c = Complaint(insured=insured, claim=claim, message="issue")
    c.full_clean()
    c.save()
    assert Complaint.objects.count() == 1

    other = Insured.objects.create(
        first_name="Bob",
        last_name="Other",
        birth_date="1991-01-01",
        cnib="CNIB654321",
    )
    c2 = Complaint(insured=other, claim=claim, message="bad")
    with pytest.raises(ValidationError):
        c2.full_clean()


@pytest.mark.django_db
def test_answer_requires_text_and_updates_status(client, prepared_claim):
    claim = prepared_claim
    complaint = Complaint.objects.create(insured=claim.policy.insured, claim=claim, message="help")
    user = User.objects.create_user(username="gest", password="pwd")
    user.userprofile.require_password_change = False
    user.userprofile.save()
    user.groups.add(Group.objects.get(name="gestionnaire"))
    assert client.login(username="gest", password="pwd")
    url = reverse("complaints:complaint_answer", args=[complaint.pk])
    # missing text
    client.post(url, {"answer_text": ""})
    complaint.refresh_from_db()
    assert complaint.status == Complaint.Status.OPEN
    # valid answer
    client.post(url, {"answer_text": "ok"})
    complaint.refresh_from_db()
    assert complaint.status == Complaint.Status.ANSWERED
    assert complaint.answer_text == "ok"


@pytest.mark.django_db
def test_close_only_after_answer(client, prepared_claim):
    claim = prepared_claim
    complaint = Complaint.objects.create(insured=claim.policy.insured, claim=claim, message="help")
    user = User.objects.create_user(username="gest", password="pwd")
    user.userprofile.require_password_change = False
    user.userprofile.save()
    user.groups.add(Group.objects.get(name="gestionnaire"))
    assert client.login(username="gest", password="pwd")
    close_url = reverse("complaints:complaint_close", args=[complaint.pk])
    resp = client.post(close_url)
    assert resp.status_code == 404
    client.post(reverse("complaints:complaint_answer", args=[complaint.pk]), {"answer_text": "ok"})
    resp = client.post(close_url)
    complaint.refresh_from_db()
    assert complaint.status == Complaint.Status.CLOSED


@pytest.mark.django_db
def test_list_view_and_filter(client, prepared_claim):
    claim = prepared_claim
    Complaint.objects.create(insured=claim.policy.insured, claim=claim, message="x")
    user = User.objects.create_user(username="comm", password="pwd")
    user.userprofile.require_password_change = False
    user.userprofile.save()
    user.groups.add(Group.objects.get(name="commercial"))
    assert client.login(username="comm", password="pwd")
    url = reverse("complaints:complaint_list")
    resp = client.get(url)
    assert resp.status_code == 200
    resp = client.get(url, {"status": Complaint.Status.OPEN})
    assert resp.status_code == 200
