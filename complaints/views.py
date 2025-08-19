from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView, CreateView, DetailView, FormView, View

from .models import Complaint
from .forms import ComplaintCreateForm, ComplaintAnswerForm
from .filters import ComplaintFilter


class ComplaintListView(ListView):
    model = Complaint
    template_name = "complaints/complaint_list.html"
    context_object_name = "complaints"

    def get_filter(self):
        return ComplaintFilter(self.request.GET, queryset=self.model.objects.select_related("insured", "claim"))

    def get_queryset(self):
        return self.get_filter().qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filter"] = self.get_filter()
        return ctx


class ComplaintCreateView(CreateView):
    model = Complaint
    form_class = ComplaintCreateForm
    template_name = "complaints/complaint_form.html"

    def get_success_url(self):
        return redirect("complaints:complaint_detail", pk=self.object.pk).url


class ComplaintDetailView(DetailView):
    model = Complaint
    template_name = "complaints/complaint_detail.html"


class ComplaintAnswerView(FormView):
    form_class = ComplaintAnswerForm
    template_name = "complaints/complaint_answer_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.complaint = get_object_or_404(Complaint, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.complaint.answer_text = form.cleaned_data["answer_text"]
        self.complaint.status = Complaint.Status.ANSWERED
        self.complaint.answered_at = timezone.now()
        if self.request.user.is_authenticated:
            self.complaint.answer_by = self.request.user
        self.complaint.save()
        return redirect("complaints:complaint_detail", pk=self.complaint.pk)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["complaint"] = self.complaint
        return ctx


class ComplaintCloseView(View):
    def post(self, request, pk):
        complaint = get_object_or_404(Complaint, pk=pk, status=Complaint.Status.ANSWERED)
        complaint.status = Complaint.Status.CLOSED
        complaint.closed_at = timezone.now()
        complaint.save()
        return redirect("complaints:complaint_detail", pk=pk)
