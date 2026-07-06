from django.contrib import admin
from .models import Asset
from import_export.admin import ImportExportModelAdmin



@admin.register(Asset)
class AssetAdmin(ImportExportModelAdmin):
    list_display = ('id', 'asset_name', 'asset_code') 
    search_fields = ('asset_name', 'asset_code')