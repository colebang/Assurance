from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from accounts.permissions import RoleRequiredMixin

from .filters import CoverageFilter, ProductFilter
from .forms import CoverageForm, ProductForm
from .models import Coverage, Product


class ProductListView(RoleRequiredMixin, ListView):
    required_roles = ("actuaire",)
    model = Product
    template_name = "catalog/product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        qs = super().get_queryset().order_by("name")
        self.filterset = ProductFilter(self.request.GET, queryset=qs)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        return context


class ProductCreateView(RoleRequiredMixin, CreateView):
    required_roles = ("actuaire",)
    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    success_url = reverse_lazy("catalog:product_list")


class ProductUpdateView(RoleRequiredMixin, UpdateView):
    required_roles = ("actuaire",)
    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    success_url = reverse_lazy("catalog:product_list")


class CoverageListView(RoleRequiredMixin, ListView):
    required_roles = ("actuaire",)
    model = Coverage
    template_name = "catalog/coverage_list.html"
    context_object_name = "coverages"

    def get_queryset(self):
        qs = super().get_queryset().select_related("product").order_by("product__name", "name")
        self.filterset = CoverageFilter(self.request.GET, queryset=qs)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        return context


class CoverageCreateView(RoleRequiredMixin, CreateView):
    required_roles = ("actuaire",)
    model = Coverage
    form_class = CoverageForm
    template_name = "catalog/coverage_form.html"
    success_url = reverse_lazy("catalog:coverage_list")


class CoverageUpdateView(RoleRequiredMixin, UpdateView):
    required_roles = ("actuaire",)
    model = Coverage
    form_class = CoverageForm
    template_name = "catalog/coverage_form.html"
    success_url = reverse_lazy("catalog:coverage_list")
