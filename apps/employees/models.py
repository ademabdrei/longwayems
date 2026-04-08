"""
Employees application models.
"""
from django.db import models
from auditlog.registry import auditlog


class Employee(models.Model):
    """
    Employee model representing company employees.
    """
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    nationality = models.CharField(max_length=50, null=True, blank=True)
    position = models.CharField(max_length=100)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    hire_date = models.DateField()
    profile_picture = models.ImageField(upload_to='employees/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employee'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status'], name='idx_employee_status'),
            models.Index(fields=['gender'], name='idx_employee_gender'),
            models.Index(fields=['position'], name='idx_employee_position'),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.position})"

    @property
    def full_name(self):
        """Return the employee's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def current_site_assignment(self):
        """Return the employee's current active site assignment."""
        return self.site_assignments.filter(status='Active').select_related('site').order_by('-start_date', '-created_at').first()

    @property
    def current_site(self):
        """Return the site the employee is currently assigned to."""
        assignment = self.current_site_assignment
        return assignment.site if assignment else None

    @property
    def current_project_assignments(self):
        """Return active project assignments within the current site."""
        return self.project_assignments.filter(status='Active').select_related('project').order_by('-created_at')


# Register model for audit logging
auditlog.register(Employee)


class EmployeeSiteAssignmentQuerySet(models.QuerySet):
    """Query helpers for site assignment history and active assignment lookups."""

    def active(self):
        return self.filter(status='Active')

    def for_employee(self, employee):
        return self.filter(employee=employee)

    def current_for_employee(self, employee):
        return self.for_employee(employee).active().order_by('-start_date', '-created_at')

    def history_for_employee(self, employee):
        return self.for_employee(employee).select_related('site').order_by('-start_date', '-created_at')

    def covering_date(self, selected_date):
        return self.filter(
            start_date__lte=selected_date
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=selected_date)
        )


class EmployeeSiteAssignmentManager(models.Manager):
    def get_queryset(self):
        return EmployeeSiteAssignmentQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def current_for_employee(self, employee):
        return self.get_queryset().current_for_employee(employee)

    def history_for_employee(self, employee):
        return self.get_queryset().history_for_employee(employee)

    def covering_date(self, selected_date):
        return self.get_queryset().covering_date(selected_date)


class EmployeeSiteAssignment(models.Model):
    """Assignment of an employee to a site."""
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
        ('Terminated', 'Terminated'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='site_assignments'
    )
    site = models.ForeignKey(
        'sites.Site',
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employee_site_assignment'
        ordering = ['-start_date']
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'site', 'start_date'],
                name='uq_emp_site_assign_emp_site_start',
            ),
        ]
        indexes = [
            models.Index(fields=['status'], name='idx_emp_site_assign_status'),
            models.Index(fields=['start_date'], name='idx_emp_site_assign_start'),
            models.Index(fields=['employee', 'status'], name='idx_emp_site_assign_emp_status'),
        ]

    objects = EmployeeSiteAssignmentManager()

    def __str__(self):
        return f"{self.employee.full_name} — {self.site.site_name}"


# Register models for audit logging
auditlog.register(EmployeeSiteAssignment)
