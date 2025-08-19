from django import forms
from django.core.exceptions import ValidationError

from .models import Claim, ClaimLine, Attachment


class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        exclude = ("reimbursable_amount", "public_code", "status", "approved_at", "reject_reason")


ClaimLineFormSet = forms.inlineformset_factory(
    Claim,
    ClaimLine,
    fields=("policy_coverage", "line_invoice_amount", "line_approved_amount"),
    extra=1,
    can_delete=True,
)


class BaseAttachmentFormSet(forms.BaseInlineFormSet):
    MAX_FILES = 5

    def clean(self):
        super().clean()
        files = 0
        for form in self.forms:
            if form.cleaned_data.get("DELETE"):
                continue
            file = form.cleaned_data.get("file")
            if file:
                files += 1
                if file.size > 5 * 1024 * 1024:
                    raise ValidationError("File too large")
                if file.content_type not in {"image/jpeg", "image/png", "application/pdf"}:
                    raise ValidationError("Invalid file type")
        if files > self.MAX_FILES:
            raise ValidationError("Too many files")


AttachmentFormSet = forms.inlineformset_factory(
    Claim,
    Attachment,
    formset=BaseAttachmentFormSet,
    fields=("file",),
    extra=1,
    can_delete=True,
)
