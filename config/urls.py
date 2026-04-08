"""
URL configuration for Employee Management System project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('sites/', include('apps.sites.urls')),
    path('employees/', include('apps.employees.urls')),
    path('projects/', include('apps.projects.urls')),
    path('attendance/', include('apps.attendance.urls')),
    path('timesheets/', include('apps.timesheets.urls')),
    path('payroll/', include('apps.payroll.urls')),
    path('documents/', include('apps.documents.urls')),
    path('', RedirectView.as_view(url='/accounts/dashboard/', permanent=False)),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
