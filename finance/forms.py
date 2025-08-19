from django import forms

from .models import Payment


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ("amount", "mode", "reference")

    def __init__(self, *args, claim, **kwargs):
        self.claim = claim
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        remaining = self.claim.reimbursable_amount - self.claim.paid_amount
        if amount is None or amount <= 0 or amount > remaining:
            raise forms.ValidationError("Invalid amount")
        return amount
