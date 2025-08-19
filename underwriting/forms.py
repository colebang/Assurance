from django import forms

from .models import Policy, Vehicle


class PolicyForm(forms.ModelForm):
    policy_number = forms.CharField(disabled=True, required=False)

    class Meta:
        model = Policy
        fields = [
            "insured",
            "product",
            "status",
            "start_date",
            "end_date",
            "vehicle",

            "premium_amount",

        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["policy_number"].initial = getattr(self.instance, "policy_number", "")


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ["insured", "plate_number", "make", "model"]
