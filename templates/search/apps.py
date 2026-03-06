"""
Search Templates Application
"""

from django.apps import AppConfig


class SearchConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'templates.search'
    verbose_name = 'Search Templates'
