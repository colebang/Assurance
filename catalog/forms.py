from django import forms

from .models import Coverage, Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "type",
            "name",
            "description",
            "default_coverage_rate",
            "waiting_days",
            "duration_days",
            "is_active",
        ]


class CoverageForm(forms.ModelForm):
    class Meta:
        model = Coverage
        fields = [
            "product",
            "name",
            "description",
            "annual_limit",
            "coverage_rate",
        ]
