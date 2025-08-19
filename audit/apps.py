from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "audit"

    def ready(self):
        from django.db.models.signals import post_save
        from django.dispatch import receiver
        from underwriting.models import Policy
        from claims.models import Claim
        from complaints.models import Complaint
        from .models import AuditLog
        from .services import audit_log

        @receiver(post_save, sender=Policy)
        def _policy_create(sender, instance, created, **kwargs):
            if created:
                audit_log(AuditLog.Action.CREATE, instance)

        @receiver(post_save, sender=Claim)
        def _claim_create(sender, instance, created, **kwargs):
            if created:
                audit_log(AuditLog.Action.CREATE, instance)

        @receiver(post_save, sender=Complaint)
        def _complaint_create(sender, instance, created, **kwargs):
            if created:
                audit_log(AuditLog.Action.CREATE, instance)
