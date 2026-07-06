from django import forms
from django.contrib.auth import get_user_model
from .models import Role, Permission


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'description', 'permissions']


class PermissionForm(forms.ModelForm):
    class Meta:
        model = Permission
        fields = ['codename', 'name', 'description']


class AssignRolesForm(forms.Form):
    user = forms.ModelChoiceField(queryset=get_user_model().objects.all())
    roles = forms.ModelMultipleChoiceField(queryset=Role.objects.all(), required=False)
