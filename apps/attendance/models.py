"""
Attendance application models.
"""
from django.db import models
from django.conf import settings
from auditlog.registry import auditlog

CustomUser = settings.AUTH_USER_MODEL


class Attendance(models.Model):
    """
    Attendance model for tracking daily employee attendance at a site.
    """
    STATUS_CHOICES = [
        ('Unmarked', 'Unmarked'),
        ('Present', 'Present'),
        ('Night', 'Night'),
        ('Double', 'Double'),
        ('Half', 'Half'),
        ('Absent', 'Absent'),
        ('On Leave', 'On Leave'),
    ]

    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    site = models.ForeignKey(
        'sites.Site',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendances'
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendances'
    )
    date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Unmarked'
    )
    overtime_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00
    )
    notes = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_attendances'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance'
        ordering = ['-date', 'employee__first_name']
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'date'],
                name='uq_attendance_employee_date',
            ),
        ]

    def __str__(self):
        site_str = f" @ {self.site.site_name}" if self.site else ""
        return f"{self.employee.full_name} — {self.date} ({self.status}){site_str}"

    def is_present(self):
        """Check if attendance status indicates presence."""
        return self.status in ['Present', 'Night', 'Double', 'Half']


# Register model for audit logging
auditlog.register(Attendance)
