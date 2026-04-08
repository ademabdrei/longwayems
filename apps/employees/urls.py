"""Employees application URL configuration."""
from django.urls import path

from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.employee_list, name='employee_list'),
    path('site/<int:site_pk>/', views.employee_list, name='employee_list_by_site'),
    path('unassigned/', views.employee_list, {'unassigned': True}, name='employee_list_unassigned'),
    path('create/', views.employee_create, name='employee_create'),
    path('modal/create/', views.employee_create_modal, name='employee_create_modal'),
    path('modal/<int:pk>/update/', views.employee_update_modal, name='employee_update_modal'),
    path('modal/<int:pk>/delete/', views.employee_delete_modal, name='employee_delete_modal'),
    path('modal/<int:pk>/site-history/', views.site_assignment_history_modal, name='site_assignment_history_modal'),
    path('<int:pk>/site-assignment/', views.site_assignment_modal, name='site_assignment_modal'),
    path('<int:pk>/site-assignment/end/', views.end_site_assignment, name='end_site_assignment'),
    path('<int:pk>/assignment/', views.assignment_modal, name='assignment_modal'),
    path('<int:pk>/assignment/end/', views.end_assignment, name='end_assignment'),
    path('<int:pk>/', views.employee_detail, name='employee_detail'),
    path('<int:pk>/update/', views.employee_update, name='employee_update'),
    path('<int:pk>/delete/', views.employee_delete, name='employee_delete'),
]
