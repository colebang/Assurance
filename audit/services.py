from .models import AuditLog


def audit_log(action, instance, *, diff=None, meta=None, user=None) -> AuditLog:
    return AuditLog.objects.create(
        object_type=instance.__class__.__name__,
        object_id=str(instance.pk),
        action=action,
        performed_by=user if getattr(user, "is_authenticated", False) else user,
        diff=diff,
        meta=meta,
    )
