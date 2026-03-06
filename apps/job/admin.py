from django.contrib import admin
from .models import Job, AIJob


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'job_type', 'salary', 'remote', 'is_ai_related', 'source_name', 'created_at']
    search_fields = ['title', 'company__name']
    list_filter = ['job_type', 'remote', 'is_ai_related', 'source_name', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AIJob)
class AIJobAdmin(admin.ModelAdmin):
    list_display = ['job', 'ai_type', 'created_at']
    search_fields = ['job__title', 'ai_type']
    list_filter = ['ai_type', 'created_at']
