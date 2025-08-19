import pytest
from django.urls import reverse
import pytest
from django.utils import timezone
from datetime import date, timedelta
from django.urls import reverse
from django.contrib.auth.models import User, Group

from catalog.models import Product, Coverage
from crm.models import Insured
from underwriting.models import Policy, PolicyCoverage
from claims.models import Claim, ClaimLine
from claims.services import compute_eligibility, approve_claim
from complaints.models import Complaint


@pytest.fixture
def sample_data():
    today = timezone.now()
    yesterday = today - timedelta(days=1)
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
    insured = Insured.objects.create(
        first_name="Alice",
        last_name="Wonder",
        birth_date="1990-01-01",
        cnib="CNIB888888",
    )
    policy_today = Policy.objects.create(
        insured=insured,
        product=product,
        start_date=today.date(),
        end_date=today.date() + timedelta(days=365),
        status=Policy.Status.ACTIVE,
    )
    PolicyCoverage.objects.get(policy=policy_today, coverage=coverage)
    policy_yesterday = Policy.objects.create(
        insured=insured,
        product=product,
        start_date=yesterday.date(),
        end_date=yesterday.date() + timedelta(days=365),
        status=Policy.Status.ACTIVE,
    )
    PolicyCoverage.objects.get(policy=policy_yesterday, coverage=coverage)
    policy_yesterday.created_at = yesterday
    policy_yesterday.save(update_fields=["created_at"])

    # Complaints
    Complaint.objects.create(insured=insured, message="issue")

    # Claims
    claim1 = Claim.objects.create(
        policy=policy_today,
        incident_at=today,
        invoice_amount=100,
    )
    ClaimLine.objects.create(claim=claim1, policy_coverage=PolicyCoverage.objects.get(policy=policy_today, coverage=coverage), line_invoice_amount=100)
    compute_eligibility(claim1)
    import time
    time.sleep(1)
    claim2 = Claim.objects.create(
        policy=policy_today,
        incident_at=today + timedelta(seconds=1),
        invoice_amount=100,
    )
    ClaimLine.objects.create(claim=claim2, policy_coverage=PolicyCoverage.objects.get(policy=policy_today, coverage=coverage), line_invoice_amount=100)
    compute_eligibility(claim2)
    approve_claim(claim2)

    return {
        "policy_today": policy_today,
        "policy_yesterday": policy_yesterday,
        "claim1": claim1,
        "claim2": claim2,
    }


@pytest.mark.django_db
def test_dashboard_counters(client, sample_data):
    user = User.objects.create_user(username="boss", password="pwd")
    user.userprofile.require_password_change = False
    user.userprofile.save()
    user.groups.add(Group.objects.get(name="dg"))
    assert client.login(username="boss", password="pwd")
    url = reverse("dashboard:dg_counters")
    resp = client.get(url)
    data = resp.json()
    assert data["policies_today"] == 1
    assert data["complaints_today"] == 1
    assert data["claims_submitted_today"] == 2
    assert data["claims_approved_today"] == 1


@pytest.mark.django_db
def test_series_policies(client, sample_data):
    user = User.objects.create_user(username="boss", password="pwd")
    user.userprofile.require_password_change = False
    user.userprofile.save()
    user.groups.add(Group.objects.get(name="dg"))
    assert client.login(username="boss", password="pwd")
    today = timezone.localdate()
    yesterday = today - timedelta(days=1)
    url = reverse("dashboard:dg_series") + f"?metric=policies&period=day&date_from={yesterday}&date_to={today}"
    resp = client.get(url)
    data = resp.json()
    assert "labels" in data and "datasets" in data
    assert len(data["labels"]) >= 2


@pytest.mark.django_db
def test_series_claims_status(client, sample_data):
    user = User.objects.create_user(username="boss2", password="pwd")
    user.userprofile.require_password_change = False
    user.userprofile.save()
    user.groups.add(Group.objects.get(name="dg"))
    assert client.login(username="boss2", password="pwd")
    url = reverse("dashboard:dg_series") + "?metric=claims_status"
    resp = client.get(url)
    data = resp.json()
    assert set(data["labels"]) >= {"SUBMITTED", "APPROVED"}


@pytest.mark.django_db
def test_dashboard_view(client):
    user = User.objects.create_user(username="boss3", password="pwd")
    user.userprofile.require_password_change = False
    user.userprofile.save()
    user.groups.add(Group.objects.get(name="dg"))
    assert client.login(username="boss3", password="pwd")
    resp = client.get(reverse("dashboard:dg_dashboard"))
    assert resp.status_code == 200
