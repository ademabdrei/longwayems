"""
Projects application URL configuration.
"""
from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('site/<int:site_pk>/', views.project_list, name='project_list_by_site'),
    path('modal/create/', views.project_create_modal, name='project_create_modal'),
    path('modal/<int:pk>/update/', views.project_update_modal, name='project_update_modal'),
    path('modal/<int:pk>/detail/', views.project_detail_modal, name='project_detail_modal'),
    path('modal/<int:pk>/delete/', views.project_delete_modal, name='project_delete_modal'),
]
