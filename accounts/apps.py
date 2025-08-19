from django.apps import AppConfig
from django.db.models.signals import post_migrate


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self) -> None:  # pragma: no cover - just import signals
        from . import signals  # noqa: F401
        from .roles import create_default_roles

        post_migrate.connect(create_default_roles)
        return super().ready()
