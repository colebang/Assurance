from django.db.models.signals import post_save
from django.dispatch import receiver

from catalog.models import Coverage

from .models import Policy, PolicyCoverage


@receiver(post_save, sender=Policy)
def create_policy_coverages(sender, instance, created, **kwargs):
    if not created:
        return
    for cov in instance.product.coverages.all():
        PolicyCoverage.objects.create(
            policy=instance,
            coverage=cov,
            annual_limit=cov.annual_limit,
            coverage_rate=cov.coverage_rate
            if cov.coverage_rate is not None
            else instance.product.default_coverage_rate,
            waiting_days=instance.product.waiting_days,
            remaining_limit=cov.annual_limit,
        )
