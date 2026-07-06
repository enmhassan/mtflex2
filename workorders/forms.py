from django import forms
from .models import WorkOrder


class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = ['title', 'eng_description', 'category', 'asset', 'priority', 'status']


class WorkOrderUpdateForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = ['title', 'eng_description', 'category', 'asset', 'priority', 'status']
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # Apply the disabled attribute to the title field's widget
    #     self.fields['title'].widget.attrs['readonly'] = True
    #     self.fields['asset'].widget.attrs['readonly'] = True
