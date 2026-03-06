from django.contrib import admin
from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'domain', 'business', 'founded', 'employees', 'created_at']
    search_fields = ['name', 'domain', 'business']
    list_filter = ['created_at', 'founded']
    readonly_fields = ['created_at', 'updated_at']
