"""
Attendance application forms.
"""
from django import forms
from .models import Attendance
from apps.employees.models import Employee
from apps.sites.models import Site


class AttendanceForm(forms.ModelForm):
    """Form for creating and updating attendance records."""

    class Meta:
        model = Attendance
        fields = [
            'employee',
            'site',
            'date',
            'status',
            'overtime_hours',
            'notes',
        ]
        widgets = {
            'employee': forms.Select(attrs={
                'class': 'form-select',
            }),
            'site': forms.Select(attrs={
                'class': 'form-select',
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'overtime_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'min': '0',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add notes (optional)'
            }),
        }


class AttendanceBulkForm(forms.Form):
    """Form for marking bulk attendance."""
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Date'
    )
    site = forms.ModelChoiceField(
        queryset=Site.objects.filter(status='Active'),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label='Site (Optional)'
    )
    employees = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.filter(status='Active'),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input',
        }),
        label='Select Employees'
    )
    status = forms.ChoiceField(
        choices=Attendance.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label='Status'
    )
    overtime_hours = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.5',
            'min': '0',
        }),
        label='Overtime Hours'
    )
