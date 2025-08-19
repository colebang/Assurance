from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import FormView, ListView

from claims.models import Claim

from .forms import PaymentForm
from .filters import PaymentFilter
from .models import Payment
from .services import pay_claim


class PaymentCreateView(FormView):
    template_name = "finance/payment_form.html"
    form_class = PaymentForm

    def dispatch(self, request, *args, **kwargs):
        self.claim = get_object_or_404(Claim, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["claim"] = self.claim
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["claim"] = self.claim
        return ctx

    def form_valid(self, form):
        pay_claim(
            self.claim,
            amount=form.cleaned_data["amount"],
            mode=form.cleaned_data["mode"],
            reference=form.cleaned_data.get("reference"),
            created_by=self.request.user if self.request.user.is_authenticated else None,
        )
        return redirect(reverse("claims:claim_detail", args=[self.claim.pk]))


class PaymentListView(ListView):
    model = Payment
    template_name = "finance/payment_list.html"
    context_object_name = "payments"

    def get_filter(self):
        return PaymentFilter(self.request.GET, queryset=Payment.objects.all())

    def get_queryset(self):
        return self.get_filter().qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filter"] = self.get_filter()
        return ctx
