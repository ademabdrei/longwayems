"""
Sites application URL configuration.
"""
from django.urls import path
from . import views

app_name = 'sites'

urlpatterns = [
    path('', views.site_list, name='site_list'),
    path('modal/create/', views.site_create_modal, name='site_create_modal'),
    path('modal/<int:pk>/update/', views.site_update_modal, name='site_update_modal'),
    path('modal/<int:pk>/detail/', views.site_detail_modal, name='site_detail_modal'),
    path('modal/<int:pk>/delete/', views.site_delete_modal, name='site_delete_modal'),
]
