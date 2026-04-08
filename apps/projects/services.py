"""Service layer for employee site assignment operations."""
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.employees.models import Employee

from apps.projects.models import Project
from apps.employees.models import EmployeeSiteAssignment


class AssignmentService:
    """Encapsulates assignment lifecycle rules and persistence."""

    @staticmethod
    def _latest_assignment(employee):
        return EmployeeSiteAssignment.objects.history_for_employee(employee).first()

    @staticmethod
    def _active_assignments(employee):
        return EmployeeSiteAssignment.objects.current_for_employee(employee)

    @classmethod
    def validate_new_assignment(cls, *, employee, site, start_date):
        latest_assignment = cls._latest_assignment(employee)
        active_assignments = cls._active_assignments(employee)

        if active_assignments.filter(site=site).exists():
            raise ValidationError('This employee already has an active assignment on the selected site.')

        if EmployeeSiteAssignment.objects.filter(employee=employee, start_date=start_date).exists():
            raise ValidationError('An assignment with this start date already exists for this employee.')

        if latest_assignment and start_date <= latest_assignment.start_date:
            raise ValidationError(
                f'Assignment start date must be later than {latest_assignment.start_date:%Y-%m-%d}.'
            )

    @classmethod
    @transaction.atomic
    def assign_site(cls, *, employee, site, start_date, status='Active', notes=''):
        cls.validate_new_assignment(employee=employee, site=site, start_date=start_date)

        active_assignments = cls._active_assignments(employee)
        close_date = start_date - timedelta(days=1)
        for assignment in active_assignments:
            assignment.status = 'Completed'
            assignment.end_date = close_date
            assignment.save(update_fields=['status', 'end_date', 'updated_at'])

        return EmployeeSiteAssignment.objects.create(
            employee=employee,
            site=site,
            start_date=start_date,
            status=status,
            notes=notes,
        )

    @staticmethod
    def validate_end_assignment(*, assignment, end_date):
        if assignment.status != 'Active':
            raise ValidationError('Only active assignments can be ended.')
        if end_date < assignment.start_date:
            raise ValidationError('End date cannot be earlier than the assignment start date.')

    @classmethod
    @transaction.atomic
    def end_assignment(cls, *, assignment, end_date):
        cls.validate_end_assignment(assignment=assignment, end_date=end_date)
        assignment.end_date = end_date
        assignment.status = 'Completed'
        assignment.save(update_fields=['end_date', 'status', 'updated_at'])
        return assignment


def assign_employee_to_site(*, employee_id, site_id, start_date, status='Active', notes=''):
    employee = Employee.objects.get(pk=employee_id)
    from apps.sites.models import Site
    site = Site.objects.get(pk=site_id)
    return AssignmentService.assign_site(
        employee=employee,
        site=site,
        start_date=start_date,
        status=status,
        notes=notes,
    )


def end_employee_assignment(*, assignment, end_date):
    return AssignmentService.end_assignment(assignment=assignment, end_date=end_date)
