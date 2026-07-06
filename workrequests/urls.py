from django.urls import path
from . import views

app_name = 'workrequests'

urlpatterns = [
    path('', views.WorkRequestListView.as_view(), name='list'),
    # path('closed/', views.ClosedWorkRequestListView.as_view(), name='closed'),
    path('create/', views.WorkRequestCreateView.as_view(), name='create'),
    path('<int:pk>/', views.WorkRequestDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.WorkRequestUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.WorkRequestDeleteView.as_view(), name='delete'),
]
