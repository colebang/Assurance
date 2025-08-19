from django.contrib.auth.views import PasswordChangeView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View


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


class PostLoginRedirectView(View):
    role_map = {
        "dg": "/dashboard/dg/",
        "rh": "/workspaces/rh/",
        "actuaire": "/workspaces/actuaire/",
        "commercial": "/workspaces/commercial/",
        "redacteur": "/workspaces/redacteur/",
        "gestionnaire": "/workspaces/gestionnaire/",
        "comptable": "/workspaces/comptable/",
    }

    def get(self, request, *args, **kwargs):
        user = request.user
        for role, url in self.role_map.items():
            if user.groups.filter(name=role).exists():
                return redirect(url)
        return redirect("/")
