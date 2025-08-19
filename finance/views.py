from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from django.views.generic import DetailView, FormView, ListView
from django.db.models import Sum

from claims.models import Claim

from .forms import PaymentForm, ReceiptForm
from .filters import PaymentFilter, PremiumFilter, ReceiptFilter
from .models import Payment, Premium, Receipt
from .services import pay_claim, receive_premium



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


class PremiumListView(ListView):
    model = Premium
    template_name = "finance/premium_list.html"
    context_object_name = "premiums"

    def get_filter(self):
        return PremiumFilter(self.request.GET, queryset=Premium.objects.all())

    def get_queryset(self):
        return self.get_filter().qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filter"] = self.get_filter()
        return ctx


class PremiumDetailView(DetailView):
    model = Premium
    template_name = "finance/premium_detail.html"
    context_object_name = "premium"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        premium = self.object
        paid = premium.receipts.aggregate(total=Sum("amount"))["total"] or 0
        ctx["paid_total"] = paid
        ctx["remaining"] = premium.amount_due - paid
        return ctx


class ReceiptCreateView(FormView):
    template_name = "finance/receipt_form.html"
    form_class = ReceiptForm

    def dispatch(self, request, *args, **kwargs):
        self.premium = get_object_or_404(Premium, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["premium"] = self.premium
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["premium"] = self.premium
        return ctx

    def form_valid(self, form):
        receive_premium(
            self.premium,
            amount=form.cleaned_data["amount"],
            mode=form.cleaned_data["mode"],
            reference=form.cleaned_data.get("reference"),
            received_by=self.request.user if self.request.user.is_authenticated else None,
        )
        return redirect(reverse("finance:premium_detail", args=[self.premium.pk]))


class ReceiptListView(ListView):
    model = Receipt
    template_name = "finance/receipt_list.html"
    context_object_name = "receipts"

    def get_filter(self):
        return ReceiptFilter(self.request.GET, queryset=Receipt.objects.select_related("premium"))

    def get_queryset(self):
        return self.get_filter().qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filter"] = self.get_filter()
        return ctx
