"""
Sites application forms.
"""
from django import forms
from .models import Site


class SiteForm(forms.ModelForm):
    """Form for creating and updating sites."""

    class Meta:
        model = Site
        fields = [
            'site_name',
            'emirate',
            'location',
            'start_date',
            'end_date',
            'manager',
            'status',
            'notes',
        ]
        widgets = {
            'site_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter site name'
            }),
            'emirate': forms.Select(attrs={
                'class': 'form-select',
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter location details'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'manager': forms.Select(attrs={
                'class': 'form-select',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes about this site'
            }),
        }
