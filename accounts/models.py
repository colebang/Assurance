from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """Additional information for :class:`~django.contrib.auth.models.User`."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="userprofile"
    )
    require_password_change = models.BooleanField(default=True)

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"Profile for {self.user}"

