import pytest
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_profile_created():
    user = User.objects.create_user(username="alice", password="temp123")
    assert user.userprofile.require_password_change is True


@pytest.mark.django_db
def test_login_redirects_to_password_change(client):
    user = User.objects.create_user(username="bob", password="temp123")
    assert client.login(username="bob", password="temp123")
    response = client.get(reverse("home"))
    assert response.status_code == 302
    assert response.url == reverse("accounts:password_change")


@pytest.mark.django_db
def test_password_change_clears_flag(client):
    user = User.objects.create_user(username="carl", password="temp123")
    assert client.login(username="carl", password="temp123")
    change_url = reverse("accounts:password_change")
    response = client.post(
        change_url,
        {
            "old_password": "temp123",
            "new_password1": "newpass123",
            "new_password2": "newpass123",
        },
        follow=True,
    )
    assert response.redirect_chain[-1][0] == reverse("accounts:password_change_done")
    user.refresh_from_db()
    assert user.userprofile.require_password_change is False
    home = client.get(reverse("home"))
    assert home.status_code == 200


@pytest.mark.django_db
def test_logout_redirects_to_login(client):
    user = User.objects.create_user(username="dave", password="temp123")
    user.userprofile.require_password_change = False
    user.userprofile.save()
    assert client.login(username="dave", password="temp123")
    response = client.get(reverse("accounts:logout"))
    assert response.status_code == 302
    assert response.url == reverse("accounts:login")
