import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from catalog.models import Coverage, Product


@pytest.mark.django_db
def test_product_creation():
    product = Product.objects.create(
        type=Product.Type.HEALTH,
        name="Health Basic",
        default_coverage_rate=0.8,
        waiting_days=0,
        duration_days=365,
    )
    assert product.pk is not None


@pytest.mark.django_db
def test_coverage_unique_per_product_name():
    product = Product.objects.create(
        type=Product.Type.AUTO,
        name="Auto Basic",
        default_coverage_rate=0.5,
        waiting_days=0,
        duration_days=365,
    )
    Coverage.objects.create(product=product, name="Damage", annual_limit=1000)
    dup = Coverage(product=product, name="Damage", annual_limit=1000)
    with pytest.raises(ValidationError):
        dup.full_clean()


@pytest.mark.django_db
def test_product_list_status_code(client):
    url = reverse("catalog:product_list")
    response = client.get(url)
    assert response.status_code == 200
