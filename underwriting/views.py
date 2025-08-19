from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
)

from .filters import PolicyFilter
from .forms import PolicyForm, VehicleForm
from .models import Policy, Vehicle


class PolicyListView(ListView):
    model = Policy
    template_name = "underwriting/policy_list.html"
    context_object_name = "policies"

    def get_queryset(self):
        qs = super().get_queryset().select_related("insured", "product").order_by("-start_date")
        self.filterset = PolicyFilter(self.request.GET, queryset=qs)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        return context


class PolicyDetailView(DetailView):
    model = Policy
    template_name = "underwriting/policy_detail.html"
    context_object_name = "policy"


class PolicyCreateView(CreateView):
    model = Policy
    form_class = PolicyForm
    template_name = "underwriting/policy_form.html"
    success_url = reverse_lazy("underwriting:policy_list")


class PolicyUpdateView(UpdateView):
    model = Policy
    form_class = PolicyForm
    template_name = "underwriting/policy_form.html"
    success_url = reverse_lazy("underwriting:policy_list")


class VehicleListView(ListView):
    model = Vehicle
    template_name = "underwriting/vehicle_list.html"
    context_object_name = "vehicles"
    queryset = Vehicle.objects.select_related("insured").order_by("plate_number")


class VehicleCreateView(CreateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = "underwriting/vehicle_form.html"
    success_url = reverse_lazy("underwriting:vehicle_list")


class VehicleUpdateView(UpdateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = "underwriting/vehicle_form.html"
    success_url = reverse_lazy("underwriting:vehicle_list")
