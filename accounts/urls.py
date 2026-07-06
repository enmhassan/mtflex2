from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('roles/', views.RoleListView.as_view(), name='role_list'),
    path('roles/add/', views.RoleCreateView.as_view(), name='role_add'),
    path('roles/<int:pk>/edit/', views.RoleUpdateView.as_view(), name='role_edit'),
    path('roles/<int:pk>/delete/', views.RoleDeleteView.as_view(), name='role_delete'),
    path('roles/assign/', views.AssignRolesView.as_view(), name='assign_roles'),

    path('permissions/', views.PermissionListView.as_view(), name='permission_list'),
    path('permissions/add/', views.PermissionCreateView.as_view(), name='permission_add'),
    path('permissions/<int:pk>/edit/', views.PermissionUpdateView.as_view(), name='permission_edit'),
    path('permissions/<int:pk>/delete/', views.PermissionDeleteView.as_view(), name='permission_delete'),
]
