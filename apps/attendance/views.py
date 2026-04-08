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
from .forms import AttendanceForm, AttendanceBulkForm


@login_required
def attendance_list(request):
    """Display list of attendance records with site sidebar filters."""
    attendances = Attendance.objects.select_related('employee', 'site', 'created_by').all()

    # Filtering
    date = request.GET.get('date')
    status = request.GET.get('status')
    employee_filter = request.GET.get('employee')
    selected_site = request.GET.get('site')
    search = request.GET.get('search')

    # Sidebar sites
    sites = Site.objects.filter(
        status__in=['Active', 'Pending', 'On Hold']
    ).annotate(
        attendance_count=Count('attendances')
    ).order_by('site_name')

    if date:
        attendances = attendances.filter(date=date)
    if status:
        attendances = attendances.filter(status=status)
    if employee_filter:
        attendances = attendances.filter(employee_id=employee_filter)
    if selected_site:
        attendances = attendances.filter(site_id=selected_site)
    if search:
        attendances = attendances.filter(
            Q(employee__first_name__icontains=search) |
            Q(employee__last_name__icontains=search) |
            Q(site__site_name__icontains=search)
        )

    # Statistics for today
    today = timezone.now().date()
    total_today = Attendance.objects.filter(date=today).count()
    present_today = Attendance.objects.filter(date=today, status__in=['Present', 'Night', 'Double', 'Half']).count()
    absent_today = Attendance.objects.filter(date=today, status='Absent').count()
    unmarked_today = Attendance.objects.filter(date=today, status='Unmarked').count()

    # Get all employees for filters
    employees = Employee.objects.filter(status='Active').order_by('first_name')

    selected_site_obj = None
    if selected_site:
        selected_site_obj = get_object_or_404(Site, pk=selected_site)

    context = {
        'attendances': attendances,
        'total_today': total_today,
        'present_today': present_today,
        'absent_today': absent_today,
        'unmarked_today': unmarked_today,
        'employees': employees,
        'sites': sites,
        'selected_site': selected_site_obj,
        'status_choices': Attendance.STATUS_CHOICES,
        'current_date': date,
        'current_status': status,
        'current_employee': employee_filter,
        'current_site': selected_site,
        'current_search': search,
        'page_title': (
            f'{selected_site_obj.site_name} Attendance' if selected_site_obj
            else 'Attendance'
        ),
    }
    return render(request, 'attendance/attendance_list.html', context)


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
            }, request=request),
        }, status=400)

    form = AttendanceForm()
    form.fields['employee'].queryset = Employee.objects.filter(status='Active')
    form.fields['site'].queryset = Site.objects.filter(status__in=['Active', 'Pending', 'On Hold'])
    return JsonResponse({
        'success': True,
        'html': render_to_string('attendance/includes/attendance_modal.html', {
            'form': form,
            'action': 'Create',
            'employees': Employee.objects.filter(status='Active').order_by('first_name'),
            'sites': Site.objects.filter(status__in=['Active', 'Pending', 'On Hold']).order_by('site_name'),
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
            }, request=request),
        }, status=400)

    form = AttendanceForm(instance=attendance)
    form.fields['employee'].queryset = Employee.objects.filter(status='Active')
    form.fields['site'].queryset = Site.objects.filter(status__in=['Active', 'Pending', 'On Hold'])
    return JsonResponse({
        'success': True,
        'html': render_to_string('attendance/includes/attendance_modal.html', {
            'form': form,
            'action': 'Update',
            'attendance': attendance,
            'employees': Employee.objects.filter(status='Active').order_by('first_name'),
            'sites': Site.objects.filter(status__in=['Active', 'Pending', 'On Hold']).order_by('site_name'),
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
