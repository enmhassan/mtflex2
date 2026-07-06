from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render
from .models import Role, Permission
from .forms import RoleForm, PermissionForm, AssignRolesForm
from .utils import require_permission
from django.contrib import messages
from django.views import View
from django.contrib.auth import authenticate, login, get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import resolve_url


class CreatorRequiredMixin(UserPassesTestMixin):
    """
    Strict ownership guard. Permits access ONLY if the logged-in user
    is the exact author/creator who submitted the specific record.
    """
    raise_exception = True  # Instantly triggers a clean HTTP 403 Forbidden page

    def test_func(self):
        user = self.request.user
        print(user)
        # 1. Deny access immediately if the user is anonymous
        if not user.is_authenticated:
            return False

        # 2. Extract the specific record target being requested
        try:
            print('trying')
            obj = self.get_object()
            print(obj)
        except AttributeError:
            print('except')
            # Safe boundary check if mixin is applied to an incompatible view type
            return False

        # 3. Dynamic field evaluation lookup (looks for your model's 'created_by' field)
        record_creator = getattr(obj, 'created_by', None)
        
        # 4. Strict equivalence validation check
        print(user)
        print(record_creator)
        return user == record_creator


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff


class RoleListView(LoginRequiredMixin, StaffRequiredMixin, generic.ListView):
    model = Role
    template_name = 'accounts/role_list.html'


class RoleCreateView(LoginRequiredMixin, StaffRequiredMixin, generic.CreateView):
    model = Role
    form_class = RoleForm
    template_name = 'accounts/role_form.html'
    success_url = reverse_lazy('accounts:role_list')


class RoleUpdateView(LoginRequiredMixin, StaffRequiredMixin, generic.UpdateView):
    model = Role
    form_class = RoleForm
    template_name = 'accounts/role_form.html'
    success_url = reverse_lazy('accounts:role_list')


class RoleDeleteView(LoginRequiredMixin, StaffRequiredMixin, generic.DeleteView):
    model = Role
    template_name = 'accounts/role_confirm_delete.html'
    success_url = reverse_lazy('accounts:role_list')


class PermissionListView(LoginRequiredMixin, StaffRequiredMixin, generic.ListView):
    model = Permission
    template_name = 'accounts/permission_list.html'


class PermissionCreateView(LoginRequiredMixin, StaffRequiredMixin, generic.CreateView):
    model = Permission
    form_class = PermissionForm
    template_name = 'accounts/permission_form.html'
    success_url = reverse_lazy('accounts:permission_list')


class PermissionUpdateView(LoginRequiredMixin, StaffRequiredMixin, generic.UpdateView):
    model = Permission
    form_class = PermissionForm
    template_name = 'accounts/permission_form.html'
    success_url = reverse_lazy('accounts:permission_list')


class PermissionDeleteView(LoginRequiredMixin, StaffRequiredMixin, generic.DeleteView):
    model = Permission
    template_name = 'accounts/permission_confirm_delete.html'
    success_url = reverse_lazy('accounts:permission_list')


class AssignRolesView(LoginRequiredMixin, StaffRequiredMixin, generic.FormView):
    template_name = 'accounts/assign_roles.html'
    form_class = AssignRolesForm
    success_url = reverse_lazy('accounts:role_list')

    def form_valid(self, form):
        user = form.cleaned_data['user']
        roles = form.cleaned_data['roles']
        user.roles.set(roles)
        user.save()
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        user_qs = self.request.GET.get('user')
        if user_qs:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                u = User.objects.get(pk=int(user_qs))
                initial['user'] = u
                initial['roles'] = u.roles.all()
            except Exception:
                pass
        return initial


class ProfileView(LoginRequiredMixin, View):
    template_name = 'accounts/profile.html'

    def get(self, request):
        form = PasswordChangeForm(request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password was updated successfully.')
            return redirect('accounts:profile')

        return render(request, self.template_name, {'form': form})


class LoginView(View):
    template_name = 'registration/login.html'


    def dispatch(self, request, *args, **kwargs):
        # Redirect authenticated users immediately to the dashboard
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {'next': request.GET.get('next', '')})

    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        User = get_user_model()
        if not User.objects.filter(username=username).exists():
            messages.error(request, 'Username does not exist.')
            return render(request, self.template_name, {'next': request.POST.get('next', '')})

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, 'Password is not correct.')
            return render(request, self.template_name, {'next': request.POST.get('next', '')})

        login(request, user)
        next_url = request.POST.get('next') or resolve_url('workorders:list')
        return redirect(next_url)
