"""
Accounts application models - Custom user authentication and roles.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from auditlog.registry import auditlog


class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser with role-based access.
    """
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
        ('Employee', 'Employee'),
    ]

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Employee')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone = models.CharField(max_length=20, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'custom_user'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role'], name='idx_custom_user_role'),
            models.Index(fields=['is_active'], name='idx_custom_user_is_active'),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"

    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}"

    def is_admin(self):
        """Check if user has Admin role."""
        return self.role == 'Admin'

    def is_manager(self):
        """Check if user has Manager role."""
        return self.role in ['Admin', 'Manager']


# Register model for audit logging
auditlog.register(CustomUser)
