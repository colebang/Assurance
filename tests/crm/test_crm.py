import pytest
import pytest
from django.urls import reverse
from django.db import IntegrityError
from django.contrib.auth.models import User, Group

from crm.models import Insured
from crm.templatetags.crm_extras import mask_cnib


@pytest.mark.django_db
def test_insured_code_generation():
    insured = Insured.objects.create(
        first_name="John",
        last_name="Doe",
        birth_date="1990-01-01",
        cnib="CNIB123456",
    )
    assert insured.code.startswith("ASS")
    assert insured.code[3:].isdigit()


@pytest.mark.django_db
def test_cnib_uniqueness():
    Insured.objects.create(
        first_name="Jane",
        last_name="Doe",
        birth_date="1990-01-01",
        cnib="CNIB000111",
    )
    with pytest.raises(IntegrityError):
        Insured.objects.create(
            first_name="Janet",
            last_name="Doe",
            birth_date="1990-01-01",
            cnib="CNIB000111",
        )


@pytest.mark.django_db
def test_insured_list_view(client):
    user = User.objects.create_user(username="comm", password="pwd")
    user.userprofile.require_password_change = False
    user.userprofile.save()
    user.groups.add(Group.objects.get(name="commercial"))
    assert client.login(username="comm", password="pwd")
    url = reverse("crm:insured_list")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_cnib_masked_in_list(client):
    insured = Insured.objects.create(
        first_name="Bob",
        last_name="Smith",
        birth_date="1990-01-01",
        cnib="CNIB999888",
    )
    user = User.objects.create_user(username="comm2", password="pwd")
    user.userprofile.require_password_change = False
    user.userprofile.save()
    user.groups.add(Group.objects.get(name="commercial"))
    assert client.login(username="comm2", password="pwd")
    url = reverse("crm:insured_list")
    response = client.get(url)
    content = response.content.decode()
    assert mask_cnib(insured.cnib) in content
    assert insured.cnib not in content
