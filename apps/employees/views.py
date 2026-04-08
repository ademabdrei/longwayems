"""Employees application views."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Count, OuterRef, Prefetch, Q, Subquery
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone

from apps.employees.models import Employee, EmployeeSiteAssignment
from apps.sites.models import Site

from .forms import EmployeeForm, SiteAssignmentForm, EndSiteAssignmentForm


def _employee_sidebar_sites():
    return Site.objects.filter(
        status__in=['Active', 'Pending', 'On Hold']
    ).annotate(
        employee_count=Count('assignments', filter=Q(assignments__status='Active'))
    ).order_by('site_name')


def _site_assignment_history(employee):
    return EmployeeSiteAssignment.objects.history_for_employee(employee)


def _current_site_assignment(employee):
    return EmployeeSiteAssignment.objects.current_for_employee(employee).select_related('site').first()


def _assignment_modal_context(employee, assign_form=None, end_form=None):
    current_assignment = _current_site_assignment(employee)
    history = _site_assignment_history(employee)
    available_sites = Site.objects.filter(
        status__in=['Active', 'Pending', 'On Hold']
    ).exclude(
        assignments__employee=employee,
        assignments__status='Active',
    ).order_by('site_name')

    assign_form = assign_form or SiteAssignmentForm(initial={
        'start_date': timezone.localdate(),
        'status': 'Active',
    })
    assign_form.fields['site'].queryset = Site.objects.filter(
        status__in=['Active', 'Pending', 'On Hold']
    ).exclude(
        pk__in=EmployeeSiteAssignment.objects.filter(
            employee=employee, status='Active'
        ).values_list('site_id', flat=True)
    ).order_by('site_name')

    end_form = end_form or EndSiteAssignmentForm(initial={
        'end_date': timezone.localdate(),
    })

    return {
        'employee': employee,
        'current_assignment': current_assignment,
        'assignment_history': history,
        'assign_form': assign_form,
        'end_form': end_form,
    }


@login_required
def employee_list(request, site_pk=None, unassigned=False):
    """Display employees with site sidebar filters and current assignment state."""
    current_assignment_qs = EmployeeSiteAssignment.objects.active().filter(
        employee=OuterRef('pk')
    ).order_by('-start_date', '-created_at')

    employees = Employee.objects.all().annotate(
        current_site_name=Subquery(current_assignment_qs.values('site__site_name')[:1]),
        current_site_id=Subquery(current_assignment_qs.values('site_id')[:1]),
        current_assignment_status=Subquery(current_assignment_qs.values('status')[:1]),
    ).order_by('first_name', 'last_name')

    status = request.GET.get('status')
    gender = request.GET.get('gender')
    search = request.GET.get('search')
    selected_site = None

    sites = _employee_sidebar_sites()
    assigned_employee_ids = EmployeeSiteAssignment.objects.active().values_list('employee_id', flat=True).distinct()

    if unassigned:
        employees = employees.exclude(id__in=assigned_employee_ids)
    elif site_pk:
        selected_site = get_object_or_404(Site, pk=site_pk)
        employees = employees.filter(
            site_assignments__site=selected_site,
            site_assignments__status='Active'
        ).distinct()

    if status:
        employees = employees.filter(status=status)
    if gender:
        employees = employees.filter(gender=gender)
    if search:
        employees = employees.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(position__icontains=search) |
            Q(current_site_name__icontains=search)
        )

    visible_employees = list(employees)
    visible_ids = [employee.pk for employee in visible_employees]
    active_assignments = EmployeeSiteAssignment.objects.active().filter(
        employee_id__in=visible_ids
    ).select_related('site')
    active_map = {assignment.employee_id: assignment for assignment in active_assignments}

    for employee in visible_employees:
        employee.current_assignment_obj = active_map.get(employee.pk)

    all_active_employees = Employee.objects.filter(status='Active')
    unassigned_count = all_active_employees.exclude(id__in=assigned_employee_ids).count()

    context = {
        'employees': visible_employees,
        'total_employees': len(visible_employees),
        'active_employees': sum(1 for employee in visible_employees if employee.status == 'Active'),
        'male_employees': sum(1 for employee in visible_employees if employee.gender == 'Male'),
        'female_employees': sum(1 for employee in visible_employees if employee.gender == 'Female'),
        'sites': sites,
        'selected_site': selected_site,
        'site_pk': site_pk,
        'show_unassigned_only': unassigned,
        'all_sites_count': all_active_employees.count(),
        'unassigned_count': unassigned_count,
        'status_choices': Employee.STATUS_CHOICES,
        'gender_choices': Employee.GENDER_CHOICES,
        'current_status': status,
        'current_gender': gender,
        'current_search': search,
        'page_title': (
            'Unassigned Employees' if unassigned
            else selected_site.site_name if selected_site
            else 'All Sites'
        ),
    }
    return render(request, 'employees/employee_list.html', context)


@login_required
def employee_create(request):
    """Create a new employee."""
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Employee "{employee.full_name}" created successfully.')
            return redirect('employees:employee_list')
    else:
        form = EmployeeForm()

    return render(request, 'employees/employee_form.html', {
        'form': form,
        'page_title': 'Create Employee',
        'action': 'Create',
    })


@login_required
def employee_detail(request, pk):
    """Display employee details and assignment history."""
    employee = get_object_or_404(Employee, pk=pk)
    current_assignment = _current_site_assignment(employee)
    assignment_history = _site_assignment_history(employee)

    return render(request, 'employees/employee_detail.html', {
        'employee': employee,
        'current_assignment': current_assignment,
        'assignment_history': assignment_history,
        'page_title': employee.full_name,
    })


@login_required
def employee_update(request, pk):
    """Update an employee."""
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f'Employee "{employee.full_name}" updated successfully.')
            return redirect('employees:employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)

    return render(request, 'employees/employee_form.html', {
        'form': form,
        'employee': employee,
        'page_title': f'Edit {employee.full_name}',
        'action': 'Update',
    })


@login_required
def employee_delete(request, pk):
    """Delete an employee."""
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        employee_name = employee.full_name
        employee.delete()
        messages.success(request, f'Employee "{employee_name}" deleted successfully.')
        return redirect('employees:employee_list')

    return render(request, 'employees/employee_confirm_delete.html', {
        'employee': employee,
        'page_title': f'Delete {employee.full_name}',
    })


@login_required
def employee_create_modal(request):
    """Create employee modal endpoint."""
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save()
            site_pk = request.POST.get('site_pk')
            if site_pk:
                try:
                    site = Site.objects.get(pk=site_pk)
                    EmployeeSiteAssignment.objects.create(
                        employee=employee,
                        site=site,
                        start_date=timezone.localdate(),
                        status='Active',
                    )
                except Site.DoesNotExist:
                    pass
            return JsonResponse({
                'success': True,
                'message': f'Employee "{employee.full_name}" created successfully.',
            })
        return JsonResponse({
            'success': False,
            'form_html': render_to_string('employees/includes/employee_form_content.html', {
                'form': form,
                'action': 'Create',
            }, request=request),
        }, status=400)

    form = EmployeeForm()
    return JsonResponse({
        'success': True,
        'html': render_to_string('employees/includes/employee_modal.html', {
            'form': form,
            'action': 'Create',
        }, request=request),
    })


@login_required
def employee_update_modal(request, pk):
    """Update employee modal endpoint."""
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': f'Employee "{employee.full_name}" updated successfully.',
            })
        return JsonResponse({
            'success': False,
            'form_html': render_to_string('employees/includes/employee_form_content.html', {
                'form': form,
                'action': 'Update',
                'employee': employee,
            }, request=request),
        }, status=400)

    form = EmployeeForm(instance=employee)
    return JsonResponse({
        'success': True,
        'html': render_to_string('employees/includes/employee_modal.html', {
            'form': form,
            'action': 'Update',
            'employee': employee,
        }, request=request),
    })


@login_required
def employee_delete_modal(request, pk):
    """Delete employee modal endpoint."""
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        employee_name = employee.full_name
        employee.delete()
        return JsonResponse({
            'success': True,
            'message': f'Employee "{employee_name}" deleted successfully.',
        })

    return JsonResponse({
        'success': True,
        'html': render_to_string('employees/includes/employee_delete_modal.html', {
            'employee': employee,
        }, request=request),
    })


@login_required
def site_assignment_history_modal(request, pk):
    """Render a modal showing the site assignment history for an employee."""
    employee = get_object_or_404(Employee, pk=pk)
    history = EmployeeSiteAssignment.objects.history_for_employee(employee)
    current_assignment = _current_site_assignment(employee)

    return JsonResponse({
        'success': True,
        'html': render_to_string('employees/includes/site_history_modal.html', {
            'employee': employee,
            'current_assignment': current_assignment,
            'site_history': history,
        }, request=request),
    })


@login_required
def site_assignment_modal(request, pk):
    """Render and process the site assignment modal for an employee."""
    employee = get_object_or_404(Employee, pk=pk)
    current_assignment = _current_site_assignment(employee)
    history = EmployeeSiteAssignment.objects.history_for_employee(employee)

    if request.method == 'POST':
        assign_form = SiteAssignmentForm(request.POST)
        available_sites_qs = Site.objects.filter(
            status__in=['Active', 'Pending', 'On Hold']
        ).exclude(
            pk__in=EmployeeSiteAssignment.objects.filter(
                employee=employee, status='Active'
            ).values_list('site_id', flat=True)
        ).order_by('site_name')
        assign_form.fields['site'].queryset = available_sites_qs

        if assign_form.is_valid():
            try:
                active_assignments = EmployeeSiteAssignment.objects.current_for_employee(employee)
                close_date = assign_form.cleaned_data['start_date']
                for assignment in active_assignments:
                    assignment.status = 'Completed'
                    assignment.end_date = close_date
                    assignment.save(update_fields=['status', 'end_date', 'updated_at'])

                EmployeeSiteAssignment.objects.create(
                    employee=employee,
                    site=assign_form.cleaned_data['site'],
                    start_date=assign_form.cleaned_data['start_date'],
                    status=assign_form.cleaned_data['status'],
                    notes=assign_form.cleaned_data.get('notes', ''),
                )
                return JsonResponse({
                    'success': True,
                    'message': f'{employee.full_name} assigned to site successfully.',
                })
            except ValidationError as exc:
                assign_form.add_error(None, exc.message)
        else:
            print(f"Form validation errors: {assign_form.errors}")
            print(f"Form data: {assign_form.data}")

        context = {
            'employee': employee,
            'current_assignment': current_assignment,
            'assignment_history': history,
            'assign_form': assign_form,
            'end_form': EndSiteAssignmentForm(initial={'end_date': timezone.localdate()}),
        }
        context['assign_form'].fields['site'].queryset = available_sites_qs
        return JsonResponse({
            'success': False,
            'html': render_to_string('employees/includes/site_assignment_modal.html', context, request=request),
        }, status=400)

    available_sites_qs = Site.objects.filter(
        status__in=['Active', 'Pending', 'On Hold']
    ).exclude(
        pk__in=EmployeeSiteAssignment.objects.filter(
            employee=employee, status='Active'
        ).values_list('site_id', flat=True)
    ).order_by('site_name')

    context = {
        'employee': employee,
        'current_assignment': current_assignment,
        'assignment_history': history,
        'assign_form': SiteAssignmentForm(initial={
            'start_date': timezone.localdate(),
            'status': 'Active',
        }),
        'end_form': EndSiteAssignmentForm(initial={'end_date': timezone.localdate()}),
    }
    context['assign_form'].fields['site'].queryset = available_sites_qs

    return JsonResponse({
        'success': True,
        'html': render_to_string('employees/includes/site_assignment_modal.html', context, request=request),
    })


@login_required
def end_site_assignment(request, pk):
    """End the active site assignment for an employee."""
    employee = get_object_or_404(Employee, pk=pk)
    current_assignment = _current_site_assignment(employee)

    if not current_assignment:
        return JsonResponse({
            'success': False,
            'message': 'This employee has no active site assignment.',
        }, status=400)

    form = EndSiteAssignmentForm(request.POST)
    if form.is_valid():
        if current_assignment.status != 'Active':
            form.add_error(None, 'Only active assignments can be ended.')
        elif form.cleaned_data['end_date'] < current_assignment.start_date:
            form.add_error(None, 'End date cannot be earlier than the assignment start date.')
        else:
            current_assignment.end_date = form.cleaned_data['end_date']
            current_assignment.status = 'Completed'
            current_assignment.save(update_fields=['end_date', 'status', 'updated_at'])
            return JsonResponse({
                'success': True,
                'message': f'Site assignment ended for {employee.full_name}.',
            })

    context = {
        'employee': employee,
        'current_assignment': current_assignment,
        'assignment_history': EmployeeSiteAssignment.objects.history_for_employee(employee),
        'assign_form': SiteAssignmentForm(initial={
            'start_date': timezone.localdate(),
            'status': 'Active',
        }),
        'end_form': form,
    }
    context['assign_form'].fields['site'].queryset = Site.objects.filter(
        status__in=['Active', 'Pending', 'On Hold']
    ).exclude(
        pk__in=EmployeeSiteAssignment.objects.filter(
            employee=employee, status='Active'
        ).values_list('site_id', flat=True)
    ).order_by('site_name')

    return JsonResponse({
        'success': False,
        'html': render_to_string('employees/includes/site_assignment_modal.html', context, request=request),
    }, status=400)


@login_required
def assignment_modal(request, pk):
    """Render and process the assign-site modal for an employee."""
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        assign_form = SiteAssignmentForm(request.POST)
        available_sites_qs = Site.objects.filter(
            status__in=['Active', 'Pending', 'On Hold']
        ).exclude(
            pk__in=EmployeeSiteAssignment.objects.filter(
                employee=employee, status='Active'
            ).values_list('site_id', flat=True)
        ).order_by('site_name')
        assign_form.fields['site'].queryset = available_sites_qs

        if assign_form.is_valid():
            try:
                # Close active site assignments
                active_assignments = EmployeeSiteAssignment.objects.current_for_employee(employee)
                close_date = assign_form.cleaned_data['start_date']
                for assignment in active_assignments:
                    assignment.status = 'Completed'
                    assignment.end_date = close_date
                    assignment.save(update_fields=['status', 'end_date', 'updated_at'])

                EmployeeSiteAssignment.objects.create(
                    employee=employee,
                    site=assign_form.cleaned_data['site'],
                    start_date=assign_form.cleaned_data['start_date'],
                    status=assign_form.cleaned_data['status'],
                    notes=assign_form.cleaned_data.get('notes', ''),
                )
                return JsonResponse({
                    'success': True,
                    'message': f'{employee.full_name} assigned successfully.',
                })
            except ValidationError as exc:
                assign_form.add_error(None, exc.message)

        context = _assignment_modal_context(employee, assign_form=assign_form)
        return JsonResponse({
            'success': False,
            'html': render_to_string('employees/includes/assignment_modal.html', context, request=request),
        }, status=400)

    context = _assignment_modal_context(employee)
    context['assign_form'].fields['site'].queryset = Site.objects.filter(
        status__in=['Active', 'Pending', 'On Hold']
    ).exclude(
        pk__in=EmployeeSiteAssignment.objects.filter(
            employee=employee, status='Active'
        ).values_list('site_id', flat=True)
    ).order_by('site_name')
    return JsonResponse({
        'success': True,
        'html': render_to_string('employees/includes/assignment_modal.html', context, request=request),
    })


@login_required
def end_assignment(request, pk):
    """End the active site assignment for an employee."""
    employee = get_object_or_404(Employee, pk=pk)
    current_assignment = _current_site_assignment(employee)

    if not current_assignment:
        return JsonResponse({
            'success': False,
            'message': 'This employee has no active assignment.',
        }, status=400)

    form = EndSiteAssignmentForm(request.POST)
    if form.is_valid():
        if current_assignment.status != 'Active':
            form.add_error(None, 'Only active assignments can be ended.')
        elif form.cleaned_data['end_date'] < current_assignment.start_date:
            form.add_error(None, 'End date cannot be earlier than the assignment start date.')
        else:
            current_assignment.end_date = form.cleaned_data['end_date']
            current_assignment.status = 'Completed'
            current_assignment.save(update_fields=['end_date', 'status', 'updated_at'])
            return JsonResponse({
                'success': True,
                'message': f'Assignment ended for {employee.full_name}.',
            })

    context = _assignment_modal_context(employee, end_form=form)
    return JsonResponse({
        'success': False,
        'html': render_to_string('employees/includes/assignment_modal.html', context, request=request),
    }, status=400)


