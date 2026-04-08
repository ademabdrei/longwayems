"""
Timesheets application models.
"""
from django.db import models
from auditlog.registry import auditlog


class Timesheet(models.Model):
    """
    Timesheet model for tracking daily work on projects within a site.
    """
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='timesheets'
    )
    site = models.ForeignKey(
        'sites.Site',
        on_delete=models.CASCADE,
        related_name='timesheets',
        null=True,
        blank=True,
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='timesheets'
    )
    date = models.DateField()
    task_description = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'timesheet'
        ordering = ['-date', 'employee__first_name']
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'project', 'date'],
                name='uq_timesheet_employee_project_date',
            ),
        ]
        indexes = [
            models.Index(fields=['employee'], name='idx_timesheet_employee'),
            models.Index(fields=['project'], name='idx_timesheet_project'),
            models.Index(fields=['site'], name='idx_timesheet_site'),
            models.Index(fields=['date'], name='idx_timesheet_date'),
        ]

    def __str__(self):
        return f"{self.employee.full_name} — {self.project.project_name} ({self.date})"


# Register model for audit logging
auditlog.register(Timesheet)
