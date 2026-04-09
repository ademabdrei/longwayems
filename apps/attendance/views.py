"""
Attendance application views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
from .models import Attendance
from apps.employees.models import Employee
from apps.sites.models import Site
from apps.projects.models import Project
from .forms import AttendanceForm, AttendanceBulkForm


@login_required
def attendance_list(request):
    """Display list of attendance records with employee-based management and date filter."""
    from datetime import timedelta

    selected_date = request.GET.get('date', timezone.now().date())
    if isinstance(selected_date, str):
        try:
            selected_date = timezone.datetime.strptime(selected_date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            selected_date = timezone.now().date()

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status = request.GET.get('status')
    selected_site = request.GET.get('site')
    selected_project = request.GET.get('project')
    search = request.GET.get('search')
    status_filter = request.GET.get('status_filter', 'all')  # all, marked, unmarked
    view_mode = request.GET.get('view_mode', 'employees')  # employees, records

    # Sidebar sites
    sites = Site.objects.filter(
        status__in=['Active', 'Pending', 'On Hold']
    ).annotate(
        attendance_count=Count('attendances')
    ).order_by('site_name')

    # Projects for filter dropdown
    projects = Project.objects.filter(
        status__in=['Active', 'Pending', 'On Hold']
    ).order_by('project_name')

    # Get employees assigned to selected site or all active employees
    employees_query = Employee.objects.filter(status='Active')

    if selected_site:
        employees_query = employees_query.filter(
            site_assignments__site_id=selected_site,
            site_assignments__status='Active'
        ).distinct()

    if search:
        employees_query = employees_query.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )

    employees_query = employees_query.order_by('first_name')
    all_employees_count = employees_query.count()

    # Build employee list with attendance status for selected date
    employees_with_attendance = []
    for emp in employees_query:
        try:
            attendance = Attendance.objects.get(employee=emp, date=selected_date)
            has_attendance = True
        except Attendance.DoesNotExist:
            attendance = None
            has_attendance = False

        # Apply status filter
        if status_filter == 'marked' and not has_attendance:
            continue
        if status_filter == 'unmarked' and has_attendance:
            continue

        # Apply project filter if selected
        if selected_project and has_attendance:
            if str(attendance.project_id) != selected_project:
                continue

        employees_with_attendance.append({
            'employee': emp,
            'attendance': attendance,
            'has_attendance': has_attendance,
        })

    # Attendance records filtering (for records view mode)
    attendances = Attendance.objects.select_related('employee', 'site', 'created_by').all()

    if date_from:
        attendances = attendances.filter(date__gte=date_from)
    if date_to:
        attendances = attendances.filter(date__lte=date_to)
    if status:
        attendances = attendances.filter(status=status)
    if selected_site:
        attendances = attendances.filter(site_id=selected_site)
    if search:
        attendances = attendances.filter(
            Q(employee__first_name__icontains=search) |
            Q(employee__last_name__icontains=search) |
            Q(site__site_name__icontains=search)
        )
    attendances = attendances.order_by('-date', '-created_at')

    # Calculate ALL stats for selected date (ignoring status filter)
    all_attendance_for_date = Attendance.objects.filter(date=selected_date)
    
    present_stats = all_attendance_for_date.filter(status='Present').count()
    absent_stats = all_attendance_for_date.filter(status='Absent').count()
    night_stats = all_attendance_for_date.filter(status='Night').count()
    double_stats = all_attendance_for_date.filter(status='Double').count()
    half_stats = all_attendance_for_date.filter(status='Half').count()
    on_leave_stats = all_attendance_for_date.filter(status='On Leave').count()

    # Calculate total overtime
    total_overtime = sum(
        float(att.overtime_hours) 
        for att in all_attendance_for_date 
        if att.overtime_hours
    )

    # Employee stats
    total_employees = len(employees_with_attendance)
    marked_count = all_attendance_for_date.count()
    unmarked_count = total_employees - marked_count
    
    print(f"STATS DEBUG - Date: {selected_date}")
    print(f"  Present: {present_stats}")
    print(f"  Absent: {absent_stats}")
    print(f"  Night: {night_stats}")
    print(f"  Double: {double_stats}")
    print(f"  Half: {half_stats}")
    print(f"  On Leave: {on_leave_stats}")
    print(f"  Total Overtime: {total_overtime}")
    print(f"  Total Employees: {total_employees}")
    print(f"  Marked: {marked_count}")
    print(f"  Unmarked: {unmarked_count}")

    selected_site_obj = None
    if selected_site:
        selected_site_obj = get_object_or_404(Site, pk=selected_site)
        # Add employee count to site
        selected_site_obj.employee_count = Employee.objects.filter(
            site_assignments__site=selected_site_obj,
            site_assignments__status='Active',
            status='Active'
        ).distinct().count()

    # Add employee count to all sites
    for site in sites:
        site.employee_count = Employee.objects.filter(
            site_assignments__site=site,
            site_assignments__status='Active',
            status='Active'
        ).distinct().count()

    # Date navigation
    today = timezone.now().date()
    prev_date = selected_date - timedelta(days=1)
    next_date = selected_date + timedelta(days=1)

    selected_project_obj = None
    if selected_project:
        selected_project_obj = get_object_or_404(Project, pk=selected_project)

    context = {
        # Employee-based management
        'employees_with_attendance': employees_with_attendance,
        'selected_date': selected_date,
        'today': today,
        'prev_date': prev_date,
        'next_date': next_date,
        'total_employees': total_employees,
        'all_employees_count': all_employees_count,
        'marked_count': marked_count,
        'unmarked_count': unmarked_count,
        'present_count': present_stats,
        'absent_count': absent_stats,
        'night_count': night_stats,
        'double_count': double_stats,
        'half_count': half_stats,
        'on_leave_count': on_leave_stats,
        'total_overtime': round(total_overtime, 1),
        'current_status_filter': status_filter,
        # Records view
        'attendances': attendances,
        'current_date_from': date_from,
        'current_date_to': date_to,
        'current_status': status,
        # Shared
        'sites': sites,
        'projects': projects,
        'selected_site': selected_site_obj,
        'selected_project': selected_project_obj,
        'status_choices': Attendance.STATUS_CHOICES,
        'current_site': selected_site,
        'current_search': search,
        'view_mode': view_mode,
        'page_title': (
            f'{selected_site_obj.site_name} Attendance' if selected_site_obj
            else 'Attendance'
        ),
    }
    return render(request, 'attendance/attendance_list.html', context)


@login_required
def manage_attendance(request):
    """Manage attendance for employees on a specific date with inline editing."""
    selected_date = request.GET.get('date', timezone.now().date())
    selected_site = request.GET.get('site')
    search = request.GET.get('search')
    status_filter = request.GET.get('status', 'all')  # all, marked, unmarked

    # Sidebar sites
    sites = Site.objects.filter(
        status__in=['Active', 'Pending', 'On Hold']
    ).annotate(
        attendance_count=Count('attendances')
    ).order_by('site_name')

    # Get employees assigned to selected site or all active employees
    employees_query = Employee.objects.filter(status='Active')
    
    if selected_site:
        employees_query = employees_query.filter(
            site_assignments__site_id=selected_site,
            site_assignments__status='Active'
        ).distinct()

    if search:
        employees_query = employees_query.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )

    employees_query = employees_query.order_by('first_name')

    # Build employee list with attendance status for selected date
    employees_with_attendance = []
    for emp in employees_query:
        try:
            attendance = Attendance.objects.get(employee=emp, date=selected_date)
            has_attendance = True
        except Attendance.DoesNotExist:
            attendance = None
            has_attendance = False

        # Apply status filter
        if status_filter == 'marked' and not has_attendance:
            continue
        if status_filter == 'unmarked' and has_attendance:
            continue

        employees_with_attendance.append({
            'employee': emp,
            'attendance': attendance,
            'has_attendance': has_attendance,
        })

    # Statistics
    total_employees = len(employees_with_attendance)
    marked_count = sum(1 for e in employees_with_attendance if e['has_attendance'])
    unmarked_count = total_employees - marked_count
    present_count = sum(1 for e in employees_with_attendance if e['attendance'] and e['attendance'].status in ['Present', 'Night', 'Double', 'Half'])
    absent_count = sum(1 for e in employees_with_attendance if e['attendance'] and e['attendance'].status == 'Absent')

    selected_site_obj = None
    if selected_site:
        selected_site_obj = get_object_or_404(Site, pk=selected_site)

    context = {
        'employees_with_attendance': employees_with_attendance,
        'selected_date': selected_date,
        'selected_site': selected_site_obj,
        'sites': sites,
        'status_choices': Attendance.STATUS_CHOICES,
        'current_search': search,
        'current_status_filter': status_filter,
        'total_employees': total_employees,
        'marked_count': marked_count,
        'unmarked_count': unmarked_count,
        'present_count': present_count,
        'absent_count': absent_count,
        'page_title': (
            f'{selected_site_obj.site_name} Attendance Management' if selected_site_obj
            else 'Attendance Management'
        ),
    }
    return render(request, 'attendance/manage_attendance.html', context)


@login_required
def quick_update_attendance(request):
    """AJAX endpoint to quickly update attendance status."""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        employee_id = request.POST.get('employee_id')
        date = request.POST.get('date', timezone.now().date())
        status = request.POST.get('status')
        overtime_hours = request.POST.get('overtime_hours', 0)
        notes = request.POST.get('notes', '')
        project_id = request.POST.get('project_id')

        employee = get_object_or_404(Employee, pk=employee_id)

        project = None
        if project_id:
            project = get_object_or_404(Project, pk=project_id)

        if status:
            attendance, created = Attendance.objects.update_or_create(
                employee=employee,
                date=date,
                defaults={
                    'status': status,
                    'overtime_hours': overtime_hours,
                    'notes': notes,
                    'project': project,
                    'created_by': request.user,
                }
            )
            return JsonResponse({
                'success': True,
                'created': created,
                'attendance_id': attendance.pk,
                'message': f'Attendance {"marked" if created else "updated"} for {employee.full_name}',
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Status is required',
            }, status=400)

    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


@login_required
def quick_mark_attendance(request):
    """AJAX endpoint to mark attendance for an employee."""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        employee_id = request.POST.get('employee_id')
        date = request.POST.get('date', timezone.now().date())
        status = request.POST.get('status', 'Present')
        site_id = request.POST.get('site_id')
        project_id = request.POST.get('project_id')
        overtime_hours = request.POST.get('overtime_hours', 0)
        notes = request.POST.get('notes', '')

        employee = get_object_or_404(Employee, pk=employee_id)

        site = None
        if site_id:
            site = get_object_or_404(Site, pk=site_id)

        project = None
        if project_id:
            project = get_object_or_404(Project, pk=project_id)

        # Convert overtime_hours to float
        try:
            overtime_hours = float(overtime_hours) if overtime_hours else 0.0
        except (ValueError, TypeError):
            overtime_hours = 0.0

        attendance, created = Attendance.objects.update_or_create(
            employee=employee,
            date=date,
            defaults={
                'status': status,
                'site': site,
                'project': project,
                'overtime_hours': overtime_hours,
                'notes': notes if notes else None,
                'created_by': request.user,
            }
        )

        return JsonResponse({
            'success': True,
            'created': created,
            'attendance_id': attendance.pk,
            'status': attendance.status,
        })

    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


@login_required
def bulk_update_attendance(request):
    """AJAX endpoint to update multiple employees at once."""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        employee_ids = request.POST.getlist('employee_ids[]')
        date = request.POST.get('date', timezone.now().date())
        status = request.POST.get('status')
        site_id = request.POST.get('site_id')
        project_id = request.POST.get('project_id')
        overtime_hours = request.POST.get('overtime_hours')
        notes = request.POST.get('notes')

        print(f"BULK UPDATE DEBUG:")
        print(f"  Employee IDs: {employee_ids}")
        print(f"  Date: {date}")
        print(f"  Status: {status}")
        print(f"  Overtime: {overtime_hours}")
        print(f"  Notes: {notes}")

        if not employee_ids:
            return JsonResponse({'success': False, 'message': 'No employees selected'}, status=400)

        # Validate status if provided
        if status:
            valid_statuses = [choice[0] for choice in Attendance.STATUS_CHOICES]
            if status not in valid_statuses:
                return JsonResponse({
                    'success': False,
                    'message': f'Invalid status: {status}. Valid choices: {valid_statuses}'
                }, status=400)

        # Convert overtime_hours to float only if provided
        if overtime_hours is not None and overtime_hours != '':
            try:
                overtime_hours = float(overtime_hours)
            except (ValueError, TypeError):
                overtime_hours = None
        else:
            overtime_hours = None

        site = None
        if site_id:
            site = get_object_or_404(Site, pk=site_id)

        project = None
        if project_id:
            project = get_object_or_404(Project, pk=project_id)

        # Get all employees at once
        employees = Employee.objects.filter(pk__in=employee_ids)
        print(f"  Found {employees.count()} employees")

        created_count = 0
        updated_count = 0
        errors = []

        for employee in employees:
            try:
                # Check if attendance exists
                attendance_exists = Attendance.objects.filter(employee=employee, date=date).exists()
                print(f"  Processing {employee.full_name} - exists: {attendance_exists}")

                # Build defaults dict - only include fields that were actually provided
                defaults = {
                    'site': site,
                    'project': project,
                    'created_by': request.user,
                }
                
                # Only update status if it was explicitly provided
                if status:
                    defaults['status'] = status
                
                # Only update overtime if it was explicitly provided
                if overtime_hours is not None:
                    defaults['overtime_hours'] = overtime_hours
                
                # Only update notes if they were explicitly provided
                if notes is not None:
                    defaults['notes'] = notes if notes else None

                attendance, created = Attendance.objects.update_or_create(
                    employee=employee,
                    date=date,
                    defaults=defaults
                )

                print(f"    -> {'Created' if created else 'Updated'} - status: {attendance.status}")

                if created:
                    created_count += 1
                else:
                    updated_count += 1
            except Exception as e:
                print(f"    -> Error: {str(e)}")
                errors.append(f'Employee {employee.full_name}: {str(e)}')

        print(f"  Result: {created_count} created, {updated_count} updated, {len(errors)} errors")
        
        success = len(errors) == 0
        return JsonResponse({
            'success': success,
            'created': created_count,
            'updated': updated_count,
            'total': len(employees),
            'errors': errors,
            'message': f'Successfully updated {len(employees)} employee(s) ({created_count} created, {updated_count} updated)',
        })

    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


@login_required
def quick_delete_attendance(request, pk):
    """AJAX endpoint to delete attendance record."""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        attendance = get_object_or_404(Attendance, pk=pk)
        employee_name = attendance.employee.full_name
        attendance.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Attendance record for {employee_name} deleted.',
        })

    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


@login_required
def quick_attendance(request, site_pk):
    """Quick attendance marking for all employees assigned to a site."""
    site = get_object_or_404(Site, pk=site_pk)
    date = request.GET.get('date', timezone.now().date())

    # Get all active employees assigned to this site
    assigned_employees = Employee.objects.filter(
        status='Active',
        site_assignments__site=site,
        site_assignments__status='Active'
    ).distinct().order_by('first_name')

    # Get existing attendance records for the selected date
    existing_attendance = Attendance.objects.filter(
        date=date,
        site=site
    ).select_related('employee')

    # Build a dict of existing attendance by employee ID
    attendance_dict = {att.employee_id: att for att in existing_attendance}

    # Build list of employees with their attendance status
    employees_with_attendance = []
    for emp in assigned_employees:
        att = attendance_dict.get(emp.pk)
        employees_with_attendance.append({
            'employee': emp,
            'attendance': att,
        })

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        action = request.POST.get('action')

        emp = get_object_or_404(Employee, pk=employee_id)

        if action == 'toggle':
            # Toggle between Present and Absent
            att, created = Attendance.objects.get_or_create(
                employee=emp,
                site=site,
                date=date,
                defaults={'status': 'Present', 'created_by': request.user}
            )
            if not created:
                # Toggle status
                new_status = 'Absent' if att.status == 'Present' else 'Present'
                att.status = new_status
                att.created_by = request.user
                att.save()
        elif action == 'mark_present':
            att, _ = Attendance.objects.update_or_create(
                employee=emp,
                site=site,
                date=date,
                defaults={'status': 'Present', 'created_by': request.user}
            )
        elif action == 'mark_absent':
            att, _ = Attendance.objects.update_or_create(
                employee=emp,
                site=site,
                date=date,
                defaults={'status': 'Absent', 'created_by': request.user}
            )

        return JsonResponse({'success': True, 'status': att.status})

    context = {
        'site': site,
        'date': date,
        'employees_with_attendance': employees_with_attendance,
        'status_choices': Attendance.STATUS_CHOICES,
    }
    return render(request, 'attendance/quick_attendance.html', context)


@login_required
def bulk_mark_site_attendance(request, site_pk):
    """Mark all employees as present for a site in one click."""
    site = get_object_or_404(Site, pk=site_pk)
    date = request.GET.get('date', timezone.now().date())

    if request.method == 'POST':
        status = request.POST.get('status', 'Present')

        # Get all active employees assigned to this site
        assigned_employees = Employee.objects.filter(
            status='Active',
            site_assignments__site=site,
            site_assignments__status='Active'
        ).distinct()

        created_count = 0
        updated_count = 0

        for emp in assigned_employees:
            att, created = Attendance.objects.update_or_create(
                employee=emp,
                site=site,
                date=date,
                defaults={
                    'status': status,
                    'created_by': request.user,
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        messages.success(request, f'Bulk attendance marked: {created_count} created, {updated_count} updated.')
        return redirect('attendance:quick_attendance', site_pk=site.pk)

    context = {
        'site': site,
        'date': date,
        'employee_count': assigned_employees.count(),
    }
    return render(request, 'attendance/bulk_mark_confirm.html', context)


@login_required
def attendance_create(request):
    """Create a new attendance record."""
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.created_by = request.user
            attendance.save()
            messages.success(request, f'Attendance marked for {attendance.employee.full_name} on {attendance.date}.')
            return redirect('attendance:attendance_list')
    else:
        form = AttendanceForm()
        form.fields['employee'].queryset = Employee.objects.filter(status='Active')
        form.fields['site'].queryset = Site.objects.filter(status__in=['Active', 'Pending', 'On Hold'])

    context = {
        'form': form,
        'page_title': 'Mark Attendance',
        'action': 'Create',
    }
    return render(request, 'attendance/attendance_form.html', context)


@login_required
def attendance_update(request, pk):
    """Update an attendance record."""
    attendance = get_object_or_404(Attendance, pk=pk)

    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.created_by = request.user
            attendance.save()
            messages.success(request, f'Attendance updated for {attendance.employee.full_name}.')
            return redirect('attendance:attendance_list')
    else:
        form = AttendanceForm(instance=attendance)
        form.fields['employee'].queryset = Employee.objects.filter(status='Active')
        form.fields['site'].queryset = Site.objects.filter(status__in=['Active', 'Pending', 'On Hold'])

    context = {
        'form': form,
        'attendance': attendance,
        'page_title': f'Edit Attendance - {attendance.employee.full_name}',
        'action': 'Update',
    }
    return render(request, 'attendance/attendance_form.html', context)


@login_required
def attendance_delete(request, pk):
    """Delete an attendance record."""
    attendance = get_object_or_404(Attendance, pk=pk)

    if request.method == 'POST':
        employee_name = attendance.employee.full_name
        attendance.delete()
        messages.success(request, f'Attendance record for {employee_name} deleted.')
        return redirect('attendance:attendance_list')

    context = {
        'attendance': attendance,
        'page_title': f'Delete Attendance - {attendance.employee.full_name}',
    }
    return render(request, 'attendance/attendance_confirm_delete.html', context)


@login_required
def bulk_attendance(request):
    """Mark attendance for multiple employees at once."""
    if request.method == 'POST':
        form = AttendanceBulkForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            site = form.cleaned_data.get('site')
            status = form.cleaned_data['status']
            overtime_hours = form.cleaned_data.get('overtime_hours', 0)
            employee_ids = form.cleaned_data.get('employees')

            created_count = 0
            updated_count = 0

            for employee_id in employee_ids:
                attendance, created = Attendance.objects.update_or_create(
                    employee_id=employee_id,
                    date=date,
                    defaults={
                        'site': site,
                        'status': status,
                        'overtime_hours': overtime_hours,
                        'created_by': request.user,
                    }
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

            messages.success(request, f'Attendance marked: {created_count} created, {updated_count} updated.')
            return redirect('attendance:attendance_list')
    else:
        form = AttendanceBulkForm()
        form.fields['employees'].queryset = Employee.objects.filter(status='Active')
        form.fields['site'].queryset = Site.objects.filter(status__in=['Active', 'Pending', 'On Hold'])

    context = {
        'form': form,
        'page_title': 'Bulk Attendance',
    }
    return render(request, 'attendance/bulk_attendance.html', context)


@login_required
def attendance_create_modal(request):
    """Create attendance modal endpoint."""
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        form.fields['employee'].queryset = Employee.objects.filter(status='Active')
        form.fields['site'].queryset = Site.objects.filter(status__in=['Active', 'Pending', 'On Hold'])
        form.fields['project'].queryset = Project.objects.filter(status__in=['Active', 'Pending', 'On Hold'])
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.created_by = request.user
            attendance.save()
            return JsonResponse({
                'success': True,
                'message': f'Attendance marked for {attendance.employee.full_name} on {attendance.date}.',
            })
        return JsonResponse({
            'success': False,
            'form_html': render_to_string('attendance/includes/attendance_form_content.html', {
                'form': form,
                'action': 'Create',
                'employees': Employee.objects.filter(status='Active').order_by('first_name'),
                'sites': Site.objects.filter(status__in=['Active', 'Pending', 'On Hold']).order_by('site_name'),
                'projects': Project.objects.filter(status__in=['Active', 'Pending', 'On Hold']).order_by('project_name'),
            }, request=request),
        }, status=400)

    form = AttendanceForm()
    form.fields['employee'].queryset = Employee.objects.filter(status='Active')
    form.fields['site'].queryset = Site.objects.filter(status__in=['Active', 'Pending', 'On Hold'])
    form.fields['project'].queryset = Project.objects.filter(status__in=['Active', 'Pending', 'On Hold'])
    return JsonResponse({
        'success': True,
        'html': render_to_string('attendance/includes/attendance_modal.html', {
            'form': form,
            'action': 'Create',
            'employees': Employee.objects.filter(status='Active').order_by('first_name'),
            'sites': Site.objects.filter(status__in=['Active', 'Pending', 'On Hold']).order_by('site_name'),
            'projects': Project.objects.filter(status__in=['Active', 'Pending', 'On Hold']).order_by('project_name'),
        }, request=request),
    })


@login_required
def attendance_update_modal(request, pk):
    """Update attendance modal endpoint."""
    attendance = get_object_or_404(Attendance, pk=pk)

    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        form.fields['employee'].queryset = Employee.objects.filter(status='Active')
        form.fields['site'].queryset = Site.objects.filter(status__in=['Active', 'Pending', 'On Hold'])
        form.fields['project'].queryset = Project.objects.filter(status__in=['Active', 'Pending', 'On Hold'])
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.created_by = request.user
            attendance.save()
            return JsonResponse({
                'success': True,
                'message': f'Attendance updated for {attendance.employee.full_name}.',
            })
        return JsonResponse({
            'success': False,
            'form_html': render_to_string('attendance/includes/attendance_form_content.html', {
                'form': form,
                'action': 'Update',
                'attendance': attendance,
                'employees': Employee.objects.filter(status='Active').order_by('first_name'),
                'sites': Site.objects.filter(status__in=['Active', 'Pending', 'On Hold']).order_by('site_name'),
                'projects': Project.objects.filter(status__in=['Active', 'Pending', 'On Hold']).order_by('project_name'),
            }, request=request),
        }, status=400)

    form = AttendanceForm(instance=attendance)
    form.fields['employee'].queryset = Employee.objects.filter(status='Active')
    form.fields['site'].queryset = Site.objects.filter(status__in=['Active', 'Pending', 'On Hold'])
    form.fields['project'].queryset = Project.objects.filter(status__in=['Active', 'Pending', 'On Hold'])
    return JsonResponse({
        'success': True,
        'html': render_to_string('attendance/includes/attendance_modal.html', {
            'form': form,
            'action': 'Update',
            'attendance': attendance,
            'employees': Employee.objects.filter(status='Active').order_by('first_name'),
            'sites': Site.objects.filter(status__in=['Active', 'Pending', 'On Hold']).order_by('site_name'),
            'projects': Project.objects.filter(status__in=['Active', 'Pending', 'On Hold']).order_by('project_name'),
        }, request=request),
    })


@login_required
def attendance_delete_modal(request, pk):
    """Delete attendance modal endpoint."""
    attendance = get_object_or_404(Attendance, pk=pk)

    if request.method == 'POST':
        employee_name = attendance.employee.full_name
        attendance.delete()
        return JsonResponse({
            'success': True,
            'message': f'Attendance record for {employee_name} deleted.',
        })

    return JsonResponse({
        'success': True,
        'html': render_to_string('attendance/includes/attendance_delete_modal.html', {
            'attendance': attendance,
        }, request=request),
    })


@login_required
def attendance_bulk_modal(request):
    """Bulk attendance modal endpoint."""
    if request.method == 'POST':
        form = AttendanceBulkForm(request.POST)
        form.fields['employees'].queryset = Employee.objects.filter(status='Active')
        form.fields['site'].queryset = Site.objects.filter(status__in=['Active', 'Pending', 'On Hold'])
        if form.is_valid():
            date = form.cleaned_data['date']
            site = form.cleaned_data.get('site')
            status = form.cleaned_data['status']
            overtime_hours = form.cleaned_data.get('overtime_hours', 0)
            employee_ids = form.cleaned_data.get('employees')

            created_count = 0
            updated_count = 0

            for employee_id in employee_ids:
                att, created = Attendance.objects.update_or_create(
                    employee_id=employee_id,
                    date=date,
                    defaults={
                        'site': site,
                        'status': status,
                        'overtime_hours': overtime_hours,
                        'created_by': request.user,
                    }
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

            return JsonResponse({
                'success': True,
                'message': f'Attendance marked: {created_count} created, {updated_count} updated.',
            })
        return JsonResponse({
            'success': False,
            'form_html': render_to_string('attendance/includes/bulk_attendance_form_content.html', {
                'form': form,
                'employees': Employee.objects.filter(status='Active').order_by('first_name'),
                'sites': Site.objects.filter(status__in=['Active', 'Pending', 'On Hold']).order_by('site_name'),
            }, request=request),
        }, status=400)

    form = AttendanceBulkForm()
    form.fields['employees'].queryset = Employee.objects.filter(status='Active')
    form.fields['site'].queryset = Site.objects.filter(status__in=['Active', 'Pending', 'On Hold'])
    return JsonResponse({
        'success': True,
        'html': render_to_string('attendance/includes/bulk_attendance_modal.html', {
            'form': form,
            'employees': Employee.objects.filter(status='Active').order_by('first_name'),
            'sites': Site.objects.filter(status__in=['Active', 'Pending', 'On Hold']).order_by('site_name'),
        }, request=request),
    })
