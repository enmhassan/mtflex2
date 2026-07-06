from django import forms
from .models import WorkRequest


class WorkRequestForm(forms.ModelForm):
    class Meta:
        model = WorkRequest
        fields = ['type', 'description', 'asset']


class WorkRequestUpdateForm(forms.ModelForm):
    class Meta:
        model = WorkRequest
        fields = ['type', 'description', 'asset']
