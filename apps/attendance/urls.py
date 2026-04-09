"""
Attendance application URL configuration.
"""
from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_list, name='attendance_list'),
    path('site/<int:site_pk>/', views.attendance_list, name='attendance_list_by_site'),
    path('site/<int:site_pk>/quick/', views.quick_attendance, name='quick_attendance'),
    path('site/<int:site_pk>/bulk-mark/', views.bulk_mark_site_attendance, name='bulk_mark_site_attendance'),
    path('create/', views.attendance_create, name='attendance_create'),
    path('<int:pk>/update/', views.attendance_update, name='attendance_update'),
    path('<int:pk>/delete/', views.attendance_delete, name='attendance_delete'),
    path('bulk/', views.bulk_attendance, name='bulk_attendance'),
    # Modal endpoints
    path('modal/create/', views.attendance_create_modal, name='attendance_create_modal'),
    path('modal/<int:pk>/update/', views.attendance_update_modal, name='attendance_update_modal'),
    path('modal/<int:pk>/delete/', views.attendance_delete_modal, name='attendance_delete_modal'),
    # AJAX quick attendance endpoints
    path('ajax/quick-mark/', views.quick_mark_attendance, name='quick_mark_attendance'),
    path('ajax/quick-update/', views.quick_update_attendance, name='quick_update_attendance'),
    path('ajax/quick-delete/<int:pk>/', views.quick_delete_attendance, name='quick_delete_attendance'),
    path('ajax/bulk-update/', views.bulk_update_attendance, name='bulk_update_attendance'),
]
