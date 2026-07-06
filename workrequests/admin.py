from django.contrib import admin
from .models import WorkRequest
from import_export.admin import ImportExportModelAdmin



@admin.register(WorkRequest)
class WorkRequestAdmin(ImportExportModelAdmin):
    list_display = ('id', 'type', 'description', 'asset', 'created_by', 'created_at') 
    search_fields = ('id', 'type', 'description', 'asset', 'created_by', 'created_at') 