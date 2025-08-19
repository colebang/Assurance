from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .filters import InsuredFilter
from .forms import InsuredForm
from .models import Insured


class InsuredListView(ListView):
    model = Insured
    template_name = "crm/insured_list.html"
    context_object_name = "insureds"

    def get_queryset(self):
        qs = super().get_queryset()
        self.filterset = InsuredFilter(self.request.GET, queryset=qs)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        return context


class InsuredCreateView(CreateView):
    model = Insured
    form_class = InsuredForm
    template_name = "crm/insured_form.html"
    success_url = reverse_lazy("crm:insured_list")


class InsuredUpdateView(UpdateView):
    model = Insured
    form_class = InsuredForm
    template_name = "crm/insured_form.html"
    success_url = reverse_lazy("crm:insured_list")


class InsuredDetailView(DetailView):
    model = Insured
    template_name = "crm/insured_detail.html"
    context_object_name = "insured"
