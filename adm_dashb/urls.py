# adminpanel/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('users/', views.manage_users, name='_adm_manage_users'),
    path('audit-logs/', views.audit_logs, name='audit_logs'),
    path('login/', views.admin_login, name='admin_login'),
    # path('add-user/', views.add_user, name='add_user'),  # Uncomment
    
    
   
]
