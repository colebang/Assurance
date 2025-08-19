from datetime import timedelta

from django.db.models import Count
from django.utils import timezone
from django.views.generic import TemplateView

from accounts.models import UserProfile
from accounts.permissions import RoleRequiredMixin
from catalog.models import Product
from complaints.models import Complaint
from crm.models import Insured
from claims.models import Claim
from finance.models import Premium
from underwriting.models import Policy


class DGWorkspaceView(RoleRequiredMixin, TemplateView):
    template_name = "workspaces/dg.html"
    required_roles = ("dg",)


class RHWorkspaceView(RoleRequiredMixin, TemplateView):
    template_name = "workspaces/rh.html"
    required_roles = ("rh",)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profiles = UserProfile.objects.filter(require_password_change=True)[:10]
        context["profiles"] = profiles
        context["password_change_required_count"] = profiles.count()
        return context


class ActuaireWorkspaceView(RoleRequiredMixin, TemplateView):
    template_name = "workspaces/actuaire.html"
    required_roles = ("actuaire",)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_products"] = Product.objects.filter(is_active=True)[:5]
        context["coverage_counts"] = (
            Product.objects.annotate(coverage_count=Count("coverages"))
            .values("name", "coverage_count")[:5]
        )
        return context


class CommercialWorkspaceView(RoleRequiredMixin, TemplateView):
    template_name = "workspaces/commercial.html"
    required_roles = ("commercial",)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        context["recent_insured"] = Insured.objects.order_by("-created_at")[:5]
        context["draft_policies"] = Policy.objects.filter(status=Policy.Status.DRAFT)[:5]
        context["expiring_policies"] = Policy.objects.filter(
            end_date__range=(today + timedelta(days=7), today + timedelta(days=30))
        )[:5]
        return context


class RedacteurWorkspaceView(RoleRequiredMixin, TemplateView):
    template_name = "workspaces/redacteur.html"
    required_roles = ("redacteur",)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["my_claims"] = Claim.objects.filter(status=Claim.Status.SUBMITTED)[:5]
        context["today_claims"] = Claim.objects.filter(
            declared_at__date=timezone.now().date()
        )[:5]
        return context


class GestionnaireWorkspaceView(RoleRequiredMixin, TemplateView):
    template_name = "workspaces/gestionnaire.html"
    required_roles = ("gestionnaire",)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["submitted_claims"] = Claim.objects.filter(status=Claim.Status.SUBMITTED)[:5]
        context["open_complaints"] = Complaint.objects.filter(status=Complaint.Status.OPEN)[:5]
        context["sla_alerts"] = Complaint.objects.filter(
            status=Complaint.Status.OPEN,
            filed_at__lt=timezone.now() - timedelta(days=7),
        )[:5]
        return context


class ComptableWorkspaceView(RoleRequiredMixin, TemplateView):
    template_name = "workspaces/comptable.html"
    required_roles = ("comptable",)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["due_premiums"] = Premium.objects.filter(
            status__in=[Premium.Status.DUE, Premium.Status.PARTIALLY_PAID]
        )[:5]
        context["approved_claims"] = Claim.objects.filter(
            status=Claim.Status.APPROVED, payments__isnull=True
        )[:5]
        return context
