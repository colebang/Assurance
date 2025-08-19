from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView

from .models import Claim
from .forms import ClaimForm, ClaimLineFormSet, AttachmentFormSet
from .filters import ClaimFilter
from .services import approve_claim, compute_eligibility


class ClaimListView(ListView):
    model = Claim
    template_name = "claims/claim_list.html"
    context_object_name = "claims"

    def get_filter(self):
        return ClaimFilter(self.request.GET, queryset=Claim.objects.all())

    def get_queryset(self):
        return self.get_filter().qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filter"] = self.get_filter()
        return ctx


class ClaimDetailView(DetailView):
    model = Claim
    template_name = "claims/claim_detail.html"
    context_object_name = "claim"


class ClaimCreateView(CreateView):
    model = Claim
    form_class = ClaimForm
    template_name = "claims/claim_form.html"
    success_url = reverse_lazy("claims:claim_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx["line_formset"] = ClaimLineFormSet(self.request.POST)
            ctx["att_formset"] = AttachmentFormSet(self.request.POST, self.request.FILES)
        else:
            ctx["line_formset"] = ClaimLineFormSet()
            ctx["att_formset"] = AttachmentFormSet()
        return ctx

    def form_valid(self, form):
        context = self.get_context_data()
        line_formset = context["line_formset"]
        att_formset = context["att_formset"]
        if line_formset.is_valid() and att_formset.is_valid():
            self.object = form.save()
            line_formset.instance = self.object
            line_formset.save()
            att_formset.instance = self.object
            for att in att_formset.save(commit=False):
                att.uploaded_by = self.request.user if self.request.user.is_authenticated else None
                att.mime = att.file.content_type
                att.size = att.file.size
                att.save()
            compute_eligibility(self.object)
            messages.success(self.request, "Claim submitted")
            return redirect(self.get_success_url())
        return self.form_invalid(form)


class ClaimApproveView(View):
    def post(self, request, pk):
        claim = get_object_or_404(Claim, pk=pk)
        approve_claim(claim)
        messages.success(request, "Claim approved")
        return redirect("claims:claim_detail", pk=pk)


class ClaimRejectView(View):
    def post(self, request, pk):
        claim = get_object_or_404(Claim, pk=pk)
        claim.status = Claim.Status.REJECTED
        claim.reject_reason = request.POST.get("reason", "")
        claim.save(update_fields=["status", "reject_reason"])
        messages.info(request, "Claim rejected")
        return redirect("claims:claim_detail", pk=pk)
