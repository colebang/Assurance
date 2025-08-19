import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.urls import reverse

from datetime import date

from catalog.models import Product, Coverage
from crm.models import Insured
from underwriting.models import Policy, PolicyCoverage, Vehicle


@pytest.fixture
def product_with_coverage():
    product = Product.objects.create(
        type=Product.Type.HEALTH,
        name="Health Basic",
        default_coverage_rate=0.8,
        waiting_days=10,
        duration_days=365,
    )
    Coverage.objects.create(
        product=product,
        name="Hospitalization",
        annual_limit=1000,
        coverage_rate=0.5,
    )
    return product


@pytest.fixture
def insured():
    return Insured.objects.create(
        first_name="Alice",
        last_name="Wonder",
        birth_date="1990-01-01",
        cnib="CNIB1234567",
    )


@pytest.mark.django_db
def test_policy_number_and_snapshots(product_with_coverage, insured):
    policy = Policy.objects.create(
        insured=insured,
        product=product_with_coverage,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
    )
    assert policy.policy_number.startswith("POL2024")
    assert PolicyCoverage.objects.filter(policy=policy).count() == 1
    pc = policy.coverages.first()
    assert pc.remaining_limit == pc.annual_limit


@pytest.mark.django_db
def test_policy_number_uniqueness(product_with_coverage, insured):
    p1 = Policy.objects.create(
        insured=insured,
        product=product_with_coverage,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
    )
    p2 = Policy.objects.create(
        insured=insured,
        product=product_with_coverage,
        start_date=date(2024, 2, 1),
        end_date=date(2024, 12, 31),
    )
    assert p1.policy_number != p2.policy_number


@pytest.mark.django_db
def test_start_date_validation(product_with_coverage, insured):
    policy = Policy(
        insured=insured,
        product=product_with_coverage,
        start_date=date(2024, 2, 1),
        end_date=date(2024, 1, 1),
    )
    with pytest.raises(ValidationError):
        policy.full_clean()


@pytest.mark.django_db
def test_vehicle_plate_uniqueness(insured):
    Vehicle.objects.create(insured=insured, plate_number="AB1234")
    with pytest.raises(IntegrityError):
        Vehicle.objects.create(insured=insured, plate_number="AB1234")


@pytest.mark.django_db
def test_policy_list_view(client):
    url = reverse("underwriting:policy_list")
    resp = client.get(url)
    assert resp.status_code == 200
