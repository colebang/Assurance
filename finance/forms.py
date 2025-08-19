from django import forms


from .models import Payment, Premium, Receipt



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



class PremiumForm(forms.ModelForm):
    class Meta:
        model = Premium
        fields = ("policy", "amount_due", "due_date", "status")
        widgets = {"policy": forms.TextInput(attrs={"readonly": "readonly"})}


class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = ("amount", "mode", "reference")

    def __init__(self, *args, premium, **kwargs):
        self.premium = premium
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        remaining = self.premium.amount_due - sum(
            r.amount for r in self.premium.receipts.all()
        )
        if amount is None or amount <= 0 or amount > remaining:
            raise forms.ValidationError("Invalid amount")
        return amount

