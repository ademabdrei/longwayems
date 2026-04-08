"""
Sites application views.
"""
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string

from .forms import SiteForm
from .models import Site
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


@login_required
def site_list(request):
    """Display list of all sites with filtering and search."""
    sites = Site.objects.all()

    status = request.GET.get('status')
    emirate = request.GET.get('emirate')
    search = request.GET.get('search')

    if status:
        sites = sites.filter(status=status)
    if emirate:
        sites = sites.filter(emirate=emirate)
    if search:
        sites = sites.filter(
            Q(site_name__icontains=search) |
            Q(location__icontains=search)
        )

    context = {
        'sites': sites,
        'total_sites': sites.count(),
        'active_sites': sites.filter(status='Active').count(),
        'completed_sites': sites.filter(status='Completed').count(),
        'status_choices': Site.STATUS_CHOICES,
        'emirate_choices': Site.EMIRATE_CHOICES,
        'current_status': status,
        'current_emirate': emirate,
        'current_search': search,
        'managers': CustomUser.objects.filter(role__in=['Admin', 'Manager']).order_by('first_name'),
        'page_title': 'Sites',
    }
    return render(request, 'sites/site_list.html', context)


@login_required
def site_create_modal(request):
    """Create site modal endpoint."""
    if request.method == 'POST':
        form = SiteForm(request.POST)
        if form.is_valid():
            site = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Site "{site.site_name}" created successfully.',
            })
        return JsonResponse({
            'success': False,
            'form_html': render_to_string('sites/includes/site_form_content.html', {
                'form': form,
                'action': 'Create',
                'managers': CustomUser.objects.filter(role__in=['Admin', 'Manager']).order_by('first_name'),
            }, request=request),
        }, status=400)

    form = SiteForm()
    return JsonResponse({
        'success': True,
        'html': render_to_string('sites/includes/site_modal.html', {
            'form': form,
            'action': 'Create',
            'managers': CustomUser.objects.filter(role__in=['Admin', 'Manager']).order_by('first_name'),
        }, request=request),
    })


@login_required
def site_update_modal(request, pk):
    """Update site modal endpoint."""
    site = get_object_or_404(Site, pk=pk)

    if request.method == 'POST':
        form = SiteForm(request.POST, instance=site)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'message': f'Site "{site.site_name}" updated successfully.',
            })
        return JsonResponse({
            'success': False,
            'form_html': render_to_string('sites/includes/site_form_content.html', {
                'form': form,
                'action': 'Update',
                'site': site,
                'managers': CustomUser.objects.filter(role__in=['Admin', 'Manager']).order_by('first_name'),
            }, request=request),
        }, status=400)

    form = SiteForm(instance=site)
    return JsonResponse({
        'success': True,
        'html': render_to_string('sites/includes/site_modal.html', {
            'form': form,
            'action': 'Update',
            'site': site,
            'managers': CustomUser.objects.filter(role__in=['Admin', 'Manager']).order_by('first_name'),
        }, request=request),
    })


@login_required
def site_detail_modal(request, pk):
    """View site details modal endpoint."""
    from datetime import date

    site = get_object_or_404(
        Site.objects.annotate(
            total_projects=Count('projects', distinct=True),
            active_projects=Count(
                'projects',
                filter=Q(projects__status='Active'),
                distinct=True
            ),
            total_employees=Count('assignments', distinct=True),
            active_employees=Count(
                'assignments',
                filter=Q(assignments__status='Active'),
                distinct=True
            ),
        ),
        pk=pk
    )

    projects = site.projects.select_related().order_by('project_name')
    active_assignments = site.assignments.filter(
        status='Active'
    ).select_related('employee').order_by('employee__first_name', 'employee__last_name')[:10]

    duration_days = None
    if site.start_date and site.end_date:
        duration_days = (site.end_date - site.start_date).days
    elif site.start_date:
        duration_days = (date.today() - site.start_date).days

    return JsonResponse({
        'success': True,
        'html': render_to_string('sites/includes/site_detail_modal.html', {
            'site': site,
            'projects': projects,
            'active_assignments': active_assignments,
            'duration_days': duration_days,
        }, request=request),
    })


@login_required
def site_delete_modal(request, pk):
    """Delete site modal endpoint."""
    site = get_object_or_404(Site, pk=pk)

    if request.method == 'POST':
        site_name = site.site_name
        site.delete()
        return JsonResponse({
            'success': True,
            'message': f'Site "{site_name}" deleted successfully.',
        })

    return JsonResponse({
        'success': True,
        'html': render_to_string('sites/includes/site_delete_modal.html', {
            'site': site,
        }, request=request),
    })
