import pytest
from django.core.exceptions import ValidationError
import pytest
from django.urls import reverse
from datetime import date
from django.contrib.auth.models import User, Group

from catalog.models import Product, Coverage
from crm.models import Insured
from underwriting.models import Policy
from finance.models import Premium
from finance.services import receive_premium


@pytest.fixture
def policy_active():
    product = Product.objects.create(
        type=Product.Type.HEALTH,
        name="Health Basic",
        default_coverage_rate=0.5,
        waiting_days=10,
        duration_days=365,
    )
    Coverage.objects.create(
        product=product,
        name="Hosp",
        annual_limit=1000,
        coverage_rate=0.5,
    )
    insured = Insured.objects.create(
        first_name="Bob",
        last_name="Lee",
        birth_date="1990-01-01",
        cnib="CNIBA1111",
    )
    policy = Policy.objects.create(
        insured=insured,
        product=product,
        start_date=date(2024,1,1),
        end_date=date(2024,12,31),
        status=Policy.Status.ACTIVE,
        premium_amount=100,
    )
    return policy


@pytest.mark.django_db
def test_premium_created_on_activation(policy_active):
    assert Premium.objects.filter(policy=policy_active).exists()


@pytest.mark.django_db
def test_receipts_update_status(policy_active):
    premium = Premium.objects.get(policy=policy_active)
    receive_premium(premium, amount=40, mode="CASH")
    premium.refresh_from_db()
    assert premium.status == Premium.Status.PARTIALLY_PAID
    receive_premium(premium, amount=60, mode="BANK")
    premium.refresh_from_db()
    assert premium.status == Premium.Status.PAID


@pytest.mark.django_db
def test_receipt_exceed_error(policy_active):
    premium = Premium.objects.get(policy=policy_active)
    with pytest.raises(ValidationError):
        receive_premium(premium, amount=200, mode="CASH")


@pytest.mark.django_db
def test_views(client, policy_active):
    user = User.objects.create_user(username="comp", password="pwd")
    user.userprofile.require_password_change = False
    user.userprofile.save()
    user.groups.add(Group.objects.get(name="comptable"))
    assert client.login(username="comp", password="pwd")
    premium = Premium.objects.get(policy=policy_active)
    resp = client.get(reverse("finance:premium_list"))
    assert resp.status_code == 200
    resp = client.get(reverse("finance:premium_detail", args=[premium.pk]))
    assert resp.status_code == 200
    resp = client.post(
        reverse("finance:receipt_create", args=[premium.pk]),
        {"amount": 10, "mode": "CASH"},
    )
    assert resp.status_code == 302
