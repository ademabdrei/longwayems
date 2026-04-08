"""
Projects application models.
"""
from django.db import models
from auditlog.registry import auditlog


class Project(models.Model):
    """
    Project model representing work within a site.
    Projects belong to a site; managers and employees are assigned to sites.
    """
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
        ('Cancelled', 'Cancelled'),
    ]

    project_name = models.CharField(max_length=200)
    site = models.ForeignKey(
        'sites.Site',
        on_delete=models.CASCADE,
        related_name='projects',
        null=True,
        blank=True,
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status'], name='idx_project_status'),
            models.Index(fields=['site'], name='idx_project_site'),
            models.Index(fields=['site', 'status'], name='idx_project_site_status'),
        ]

    def __str__(self):
        site_str = f" ({self.site.site_name})" if self.site else ""
        return f"{self.project_name}{site_str}"


class EmployeeProjectAssignment(models.Model):
    """Tracks which projects an employee works on within their assigned site."""
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
        ('Terminated', 'Terminated'),
    ]

    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='project_assignments'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='employee_assignments'
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employee_project_assignment'
        ordering = ['-start_date']
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'project', 'start_date'],
                name='uq_emp_proj_assignment_emp_proj_start',
            ),
        ]
        indexes = [
            models.Index(fields=['status'], name='idx_emp_proj_assign_status'),
            models.Index(fields=['start_date'], name='idx_emp_proj_assign_start'),
            models.Index(fields=['employee', 'status'], name='idx_emp_proj_assign_emp_status'),
        ]

    def __str__(self):
        return f"{self.employee.full_name} — {self.project.project_name}"


# Register models for audit logging
auditlog.register(Project)
auditlog.register(EmployeeProjectAssignment)
