"""
Accounts application views - Authentication and dashboard.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .forms import LoginForm, UserForm

CustomUser = get_user_model()


def login_view(request):
    """
    Handle user login with session authentication.
    Redirects to dashboard if already logged in.
    """
    if request.user.is_authenticated:
        return redirect('accounts:admin_dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Check if user is Admin
            if user.role != 'Admin':
                messages.error(request, 'You do not have permission to access the admin panel.')
                logout(request)
                return redirect('accounts:login')
            
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('accounts:admin_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """
    Handle user logout.
    """
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


def admin_dashboard_view(request):
    """
    Admin dashboard - only accessible by Admin users.
    """
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    if request.user.role != 'Admin':
        messages.error(request, 'You do not have permission to access the admin dashboard.')
        logout(request)
        return redirect('accounts:login')

    # Import models for stats
    from apps.employees.models import Employee, EmployeeSiteAssignment
    from apps.sites.models import Site
    from apps.projects.models import Project
    from django.contrib.auth import get_user_model

    CustomUser = get_user_model()

    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(status='Active').count()
    inactive_employees = Employee.objects.filter(status='Inactive').count()
    assigned_employees = EmployeeSiteAssignment.objects.filter(status='Active').values_list('employee_id', flat=True).distinct().count()
    unassigned_employees = active_employees - assigned_employees

    total_sites = Site.objects.count()
    active_sites = Site.objects.filter(status='Active').count()
    completed_sites = Site.objects.filter(status='Completed').count()

    total_projects = Project.objects.count()
    active_projects = Project.objects.filter(status='Active').count()

    recent_employees = Employee.objects.select_related().order_by('-created_at')[:5]
    recent_sites = Site.objects.order_by('-created_at')[:5]
    active_site_assignments = EmployeeSiteAssignment.objects.filter(
        status='Active'
    ).select_related('employee', 'site').order_by('-created_at')[:5]

    context = {
        'page_title': 'Admin Dashboard',
        'user': request.user,
        'total_employees': total_employees,
        'active_employees': active_employees,
        'inactive_employees': inactive_employees,
        'assigned_employees': assigned_employees,
        'unassigned_employees': unassigned_employees,
        'total_sites': total_sites,
        'active_sites': active_sites,
        'completed_sites': completed_sites,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'total_users': CustomUser.objects.count(),
        'recent_employees': recent_employees,
        'recent_sites': recent_sites,
        'active_site_assignments': active_site_assignments,
        'managers': CustomUser.objects.filter(role__in=['Admin', 'Manager']).order_by('first_name'),
        'emirate_choices': Site.EMIRATE_CHOICES,
        'site_status_choices': Site.STATUS_CHOICES,
    }
    return render(request, 'accounts/admin_dashboard.html', context)


@login_required
def user_list(request):
    """Display list of all users with filtering and search."""
    users = CustomUser.objects.all()
    
    # Filtering
    role = request.GET.get('role')
    status = request.GET.get('status')
    search = request.GET.get('search')
    
    if role:
        users = users.filter(role=role)
    if status:
        users = users.filter(is_active=(status == 'Active'))
    if search:
        users = users.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(username__icontains=search)
        )
    
    # Statistics
    total_users = users.count()
    admin_users = users.filter(role='Admin').count()
    manager_users = users.filter(role='Manager').count()
    employee_users = users.filter(role='Employee').count()
    active_users = users.filter(is_active=True).count()
    
    context = {
        'users': users,
        'total_users': total_users,
        'admin_users': admin_users,
        'manager_users': manager_users,
        'employee_users': employee_users,
        'active_users': active_users,
        'role_choices': CustomUser.ROLE_CHOICES,
        'current_role': role,
        'current_status': status,
        'current_search': search,
        'page_title': 'Users',
    }
    return render(request, 'accounts/user_list.html', context)


@login_required
def user_create(request):
    """Create a new user."""
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            messages.success(request, f'User "{user.full_name}" created successfully.')
            return redirect('accounts:user_list')
    else:
        form = UserForm()
    
    context = {
        'form': form,
        'page_title': 'Create User',
        'action': 'Create',
    }
    return render(request, 'accounts/user_form.html', context)


@login_required
def user_update(request, pk):
    """Update an existing user."""
    user = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            messages.success(request, f'User "{user.full_name}" updated successfully.')
            return redirect('accounts:user_list')
    else:
        form = UserForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
        'page_title': f'Edit {user.full_name}',
        'action': 'Update',
    }
    return render(request, 'accounts/user_form.html', context)


@login_required
def user_delete(request, pk):
    """Delete a user."""
    user = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        user_name = user.full_name
        user.delete()
        messages.success(request, f'User "{user_name}" deleted successfully.')
        return redirect('accounts:user_list')
    
    context = {
        'user': user,
        'page_title': f'Delete {user.full_name}',
    }
    return render(request, 'accounts/user_confirm_delete.html', context)
