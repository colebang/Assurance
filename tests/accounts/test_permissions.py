import pytest
from datetime import date
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User, Group

from catalog.models import Product, Coverage
from crm.models import Insured
from underwriting.models import Policy, PolicyCoverage
from claims.models import Claim, ClaimLine
from claims.services import compute_eligibility, approve_claim


@pytest.fixture
def claim_obj(db):
    product = Product.objects.create(
        type=Product.Type.HEALTH,
        name="Health",
        default_coverage_rate=0.5,
        waiting_days=0,
        duration_days=365,
    )
    coverage = Coverage.objects.create(
        product=product,
        name="Basic",
        annual_limit=1000,
        coverage_rate=0.5,
    )
    insured = Insured.objects.create(
        first_name="Alice",
        last_name="Wonder",
        birth_date="1990-01-01",
        cnib="CNIB999999",
    )
    policy = Policy.objects.create(
        insured=insured,
        product=product,
        start_date=date(2024,1,1),
        end_date=date(2024,12,31),
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
def test_redacteur_cannot_approve(client, claim_obj):
    user = User.objects.create_user(username="red", password="pwd")
    user.userprofile.require_password_change = False
    user.userprofile.save()
    user.groups.add(Group.objects.get(name="redacteur"))
    assert client.login(username="red", password="pwd")
    # can access claim list
    assert client.get(reverse("claims:claim_list")).status_code == 200
    # cannot approve
    resp = client.post(reverse("claims:claim_approve", args=[claim_obj.pk]))
    assert resp.status_code == 403


@pytest.mark.django_db
def test_gestionnaire_can_approve_and_see_amounts(client, claim_obj):
    user = User.objects.create_user(username="gest", password="pwd")
    user.userprofile.require_password_change = False
    user.userprofile.save()
    user.groups.add(Group.objects.get(name="gestionnaire"))
    assert client.login(username="gest", password="pwd")
    detail = client.get(reverse("claims:claim_detail", args=[claim_obj.pk]))
    assert str(int(claim_obj.reimbursable_amount)) in detail.content.decode()
    resp = client.post(reverse("claims:claim_approve", args=[claim_obj.pk]))
    assert resp.status_code in (302, 200)


@pytest.mark.django_db
def test_comptable_payment_access(client, claim_obj):
    approve_claim(claim_obj)
    comp = User.objects.create_user(username="comp", password="pwd")
    comp.userprofile.require_password_change = False
    comp.userprofile.save()
    comp.groups.add(Group.objects.get(name="comptable"))
    assert client.login(username="comp", password="pwd")
    url = reverse("finance:payment_create", args=[claim_obj.pk])
    assert client.get(url).status_code == 200
    client.logout()
    comm = User.objects.create_user(username="comm", password="pwd")
    comm.userprofile.require_password_change = False
    comm.userprofile.save()
    comm.groups.add(Group.objects.get(name="commercial"))
    assert client.login(username="comm", password="pwd")
    assert client.get(url).status_code == 403


@pytest.mark.django_db
def test_dg_dashboard_permissions(client):
    boss = User.objects.create_user(username="boss", password="pwd")
    boss.userprofile.require_password_change = False
    boss.userprofile.save()
    boss.groups.add(Group.objects.get(name="dg"))
    assert client.login(username="boss", password="pwd")
    assert client.get(reverse("dashboard:dg_dashboard")).status_code == 200
    assert client.get(reverse("catalog:product_create")).status_code == 403
