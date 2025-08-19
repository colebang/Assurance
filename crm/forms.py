from django import forms

from .models import Insured


class InsuredForm(forms.ModelForm):
    code = forms.CharField(disabled=True, required=False)

    class Meta:
        model = Insured
        fields = [
            "first_name",
            "last_name",
            "birth_date",
            "cnib",
            "phone",
            "email",
        ]

    field_order = [
        "code",
        "first_name",
        "last_name",
        "birth_date",
        "cnib",
        "phone",
        "email",
    ]
