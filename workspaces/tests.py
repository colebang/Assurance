import pytest
from django.contrib.auth.models import Group
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    "group_name,expected",
    [
        ("dg", "/dashboard/dg/"),
        ("rh", "/workspaces/rh/"),
        ("actuaire", "/workspaces/actuaire/"),
        ("commercial", "/workspaces/commercial/"),
        ("redacteur", "/workspaces/redacteur/"),
        ("gestionnaire", "/workspaces/gestionnaire/"),
        ("comptable", "/workspaces/comptable/"),
    ],
)
def test_post_login_redirects(client, django_user_model, group_name, expected):
    user = django_user_model.objects.create_user(username=group_name, password="pwd")
    user.userprofile.require_password_change = False
    user.userprofile.save()
    group, _ = Group.objects.get_or_create(name=group_name)
    user.groups.add(group)
    client.force_login(user)
    response = client.get(reverse("workspaces:me"))
    assert response.status_code == 302
    assert response.url == expected


@pytest.mark.django_db
def test_post_login_redirect_default(client, django_user_model):
    user = django_user_model.objects.create_user(username="no-role", password="pwd")
    user.userprofile.require_password_change = False
    user.userprofile.save()
    client.force_login(user)
    response = client.get(reverse("workspaces:me"))
    assert response.status_code == 302
    assert response.url == "/"


@pytest.mark.django_db
def test_role_required_mixin(client, django_user_model):
    user = django_user_model.objects.create_user(username="test", password="pwd")
    user.userprofile.require_password_change = False
    user.userprofile.save()
    client.force_login(user)
    assert client.get(reverse("workspaces:rh")).status_code == 403
    group, _ = Group.objects.get_or_create(name="rh")
    user.groups.add(group)
    assert client.get(reverse("workspaces:rh")).status_code == 200
