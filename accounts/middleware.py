from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class ForcePasswordChangeMiddleware:
    """Redirect users to password change page until they update their password."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            profile = getattr(user, "userprofile", None)
            if profile and profile.require_password_change:
                allowed = {
                    reverse("accounts:password_change"),
                    reverse("accounts:password_change_done"),
                    reverse("accounts:logout"),
                    reverse("accounts:login"),
                }
                if request.path not in allowed and not request.path.startswith(settings.STATIC_URL) and not request.path.startswith(settings.MEDIA_URL):
                    return redirect("accounts:password_change")
        return self.get_response(request)
