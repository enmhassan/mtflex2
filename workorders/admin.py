from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import WorkOrder


def export_workorders_as_csv(modeladmin, request, queryset):
    """Admin action to export selected WorkOrder objects as CSV."""
    fieldnames = ['id', 'title', 'description', 'category', 'priority', 'created_by', 'created_at', 'status']
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=workorders_export.csv'
    writer = csv.writer(response)
    writer.writerow(fieldnames)
    for wo in queryset.order_by('id'):
        writer.writerow([
            wo.pk,
            wo.title,
            wo.description,
            wo.category,
            wo.priority,
            wo.created_by.username if wo.created_by else '',
            wo.created_at.isoformat() if wo.created_at else '',
            wo.status,
        ])
    return response
export_workorders_as_csv.short_description = 'Export selected workorders as CSV'


class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_by', 'created_at', 'category', 'priority', 'status')
    list_filter = ('status', 'priority', 'status')
    search_fields = ('title', 'description', 'category')
    actions = [export_workorders_as_csv]


admin.site.register(WorkOrder, WorkOrderAdmin)
