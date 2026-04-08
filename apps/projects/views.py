"""Projects application views."""
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string

from apps.sites.models import Site

from .forms import ProjectForm
from .models import Project

CustomUser = get_user_model()


@login_required
def project_list(request, site_pk=None):
    """Display projects with site sidebar filters."""
    projects = Project.objects.select_related('site', 'site__manager').all()

    status = request.GET.get('status')
    search = request.GET.get('search')
    selected_site = None

    if status:
        projects = projects.filter(status=status)
    if search:
        projects = projects.filter(
            Q(project_name__icontains=search)
        )
    if site_pk:
        selected_site = get_object_or_404(Site, pk=site_pk)
        projects = projects.filter(site=selected_site)

    from django.db.models.functions import Now
    from datetime import date

    projects = projects.annotate(
        total_employees=Count('employee_assignments', distinct=True),
        active_employees=Count(
            'employee_assignments',
            filter=Q(employee_assignments__status='Active'),
            distinct=True
        ),
    )

    sites = Site.objects.filter(
        status__in=['Active', 'Pending', 'On Hold']
    ).annotate(
        project_count=Count('projects')
    ).order_by('site_name')

    all_projects_count = Project.objects.count()

    context = {
        'projects': projects,
        'total_projects': projects.count(),
        'active_projects': projects.filter(status='Active').count(),
        'completed_projects': projects.filter(status='Completed').count(),
        'on_hold_projects': projects.filter(status='On Hold').count(),
        'status_choices': Project.STATUS_CHOICES,
        'sites': sites,
        'selected_site': selected_site,
        'site_pk': site_pk,
        'all_sites_count': all_projects_count,
        'current_status': status,
        'current_search': search,
        'page_title': selected_site.site_name if selected_site else 'All Sites',
    }
    return render(request, 'projects/project_list.html', context)


@login_required
def project_create_modal(request):
    """Create project modal endpoint."""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Project "{project.project_name}" created successfully.',
            })
        return JsonResponse({
            'success': False,
            'form_html': render_to_string('projects/includes/project_form_content.html', {
                'form': form,
                'action': 'Create',
                'sites': form.fields['site'].queryset,
            }, request=request),
        }, status=400)

    form = ProjectForm()
    form.fields['site'].queryset = form.fields['site'].queryset.order_by('site_name')
    return JsonResponse({
        'success': True,
        'html': render_to_string('projects/includes/project_modal.html', {
            'form': form,
            'action': 'Create',
            'sites': form.fields['site'].queryset,
        }, request=request),
    })


@login_required
def project_update_modal(request, pk):
    """Update project modal endpoint."""
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': f'Project "{project.project_name}" updated successfully.',
            })
        return JsonResponse({
            'success': False,
            'form_html': render_to_string('projects/includes/project_form_content.html', {
                'form': form,
                'action': 'Update',
                'project': project,
                'sites': form.fields['site'].queryset,
            }, request=request),
        }, status=400)

    form = ProjectForm(instance=project)
    form.fields['site'].queryset = form.fields['site'].queryset.order_by('site_name')
    return JsonResponse({
        'success': True,
        'html': render_to_string('projects/includes/project_modal.html', {
            'form': form,
            'action': 'Update',
            'project': project,
            'sites': form.fields['site'].queryset,
        }, request=request),
    })


@login_required
def project_detail_modal(request, pk):
    """View project details modal endpoint."""
    from datetime import date
    from django.db.models import Prefetch

    project = get_object_or_404(
        Project.objects.annotate(
            total_employees=Count('employee_assignments', distinct=True),
            active_employees=Count(
                'employee_assignments',
                filter=Q(employee_assignments__status='Active'),
                distinct=True
            ),
        ),
        pk=pk
    )

    active_assignments = project.employee_assignments.filter(
        status='Active'
    ).select_related('employee').order_by('employee__first_name', 'employee__last_name')

    all_assignments = project.employee_assignments.select_related(
        'employee'
    ).order_by('-start_date', '-created_at')[:10]

    duration_days = None
    if project.start_date and project.end_date:
        duration_days = (project.end_date - project.start_date).days
    elif project.start_date:
        duration_days = (date.today() - project.start_date).days

    return JsonResponse({
        'success': True,
        'html': render_to_string('projects/includes/project_detail_modal.html', {
            'project': project,
            'active_assignments': active_assignments,
            'recent_assignments': all_assignments,
            'duration_days': duration_days,
        }, request=request),
    })


@login_required
def project_delete_modal(request, pk):
    """Delete project modal endpoint."""
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        project_name = project.project_name
        project.delete()
        return JsonResponse({
            'success': True,
            'message': f'Project "{project_name}" deleted successfully.',
        })

    return JsonResponse({
        'success': True,
        'html': render_to_string('projects/includes/project_delete_modal.html', {
            'project': project,
        }, request=request),
    })
