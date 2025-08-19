from django.contrib.auth.views import PasswordChangeView, LogoutView
from django.urls import reverse_lazy


class ForcePasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy("accounts:password_change_done")

    def form_valid(self, form):
        response = super().form_valid(form)
        profile = self.request.user.userprofile
        profile.require_password_change = False
        profile.save()
        return response


class SimpleLogoutView(LogoutView):
    """Allow GET requests for logout to simplify navigation in tests."""

    next_page = reverse_lazy("accounts:login")
    http_method_names = ["get", "post", "head", "options"]

    def get(self, request, *args, **kwargs):  # pragma: no cover - thin wrapper
        return self.post(request, *args, **kwargs)
