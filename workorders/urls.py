from django.urls import path
from . import views

app_name = 'workorders'

urlpatterns = [
    path('', views.WorkOrderListView.as_view(), name='list'),
    path('closed/', views.ClosedWorkOrderListView.as_view(), name='closed'),
    path('create/', views.WorkOrderCreateView.as_view(), name='create'),
    # Chat and retrain routes removed
    path('<int:pk>/', views.WorkOrderDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.WorkOrderUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.WorkOrderDeleteView.as_view(), name='delete'),
    path('<int:request_id>/convert/', views.ConvertRequestToOrderView.as_view(), name='convert_request_to_order'),
    path('monthly-report/', views.MonthlyWorkOrderReportView.as_view(), name='monthly_report'),
]
