"""
API URL Configuration
"""

from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('search_company', views.search_company, name='search_company'),
    path('company/<int:company_id>', views.get_company, name='get_company'),
    path('health', views.health_check, name='health_check'),
]
