"""
Employees application forms.
"""
from django import forms
from .models import Employee, EmployeeSiteAssignment
from apps.sites.models import Site


class EmployeeForm(forms.ModelForm):
    """Form for creating and updating employees."""

    class Meta:
        model = Employee
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone',
            'gender',
            'nationality',
            'position',
            'basic_salary',
            'hire_date',
            'profile_picture',
            'status',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select',
            }),
            'nationality': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter nationality'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter job position'
            }),
            'basic_salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'profile_picture': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
        }


class SiteAssignmentForm(forms.Form):
    """Form for creating a new employee site assignment."""

    site = forms.ModelChoiceField(
        queryset=Site.objects.filter(status__in=['Active', 'Pending', 'On Hold']).order_by('site_name'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Site'
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Start Date'
    )
    status = forms.ChoiceField(
        choices=EmployeeSiteAssignment.STATUS_CHOICES,
        initial='Active',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Status'
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional assignment notes'
        }),
        label='Notes'
    )


class EndSiteAssignmentForm(forms.Form):
    """Form for ending the current active site assignment."""

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='End Date'
    )
