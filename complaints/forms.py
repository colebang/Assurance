from django import forms

from .models import Complaint


class ComplaintCreateForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["insured", "claim", "message"]


class ComplaintAnswerForm(forms.ModelForm):
    answer_text = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = Complaint
        fields = ["answer_text"]
