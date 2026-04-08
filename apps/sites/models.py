"""
Sites application models.
"""
from django.conf import settings
from django.db import models
from auditlog.registry import auditlog

CustomUser = settings.AUTH_USER_MODEL


class Site(models.Model):
    """
    Top-level organizational unit — a physical site/location.
    Managers and employees are assigned to sites.
    Projects live within sites.
    """
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
        ('Cancelled', 'Cancelled'),
    ]

    EMIRATE_CHOICES = [
        ('Abu Dhabi', 'Abu Dhabi'),
        ('Dubai', 'Dubai'),
        ('Sharjah', 'Sharjah'),
        ('Ajman', 'Ajman'),
        ('Umm Al Quwain', 'Umm Al Quwain'),
        ('Ras Al Khaimah', 'Ras Al Khaimah'),
        ('Fujairah', 'Fujairah'),
    ]

    site_name = models.CharField(max_length=200)
    emirate = models.CharField(max_length=50, choices=EMIRATE_CHOICES, null=True, blank=True)
    location = models.CharField(max_length=300, null=True, blank=True)
    manager = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_sites',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'site'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status'], name='idx_site_status'),
            models.Index(fields=['emirate'], name='idx_site_emirate'),
            models.Index(fields=['status', 'emirate'], name='idx_site_status_emirate'),
        ]

    def __str__(self):
        return self.site_name

    @property
    def active_project_count(self):
        return self.projects.filter(status='Active').count()

    @property
    def active_employee_count(self):
        from django.db.models import Count
        return self.assignments.filter(status='Active').values('employee').distinct().count()


# Register model for audit logging
auditlog.register(Site)
