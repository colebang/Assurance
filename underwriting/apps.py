from django.apps import AppConfig


class UnderwritingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "underwriting"

    def ready(self):  # pragma: no cover - import signals
        import underwriting.signals  # noqa
