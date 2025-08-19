from django.contrib.auth.mixins import UserPassesTestMixin


class RoleRequiredMixin(UserPassesTestMixin):
    required_roles: tuple[str, ...] = ()

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.is_superuser or user.groups.filter(name__in=self.required_roles).exists()
        )
