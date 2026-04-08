"""
Documents application models.
"""
from django.db import models
from auditlog.registry import auditlog


class Document(models.Model):
    """
    Document model for storing employee, site, and project related files.
    """
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )
    site = models.ForeignKey(
        'sites.Site',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )
    document_type = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='documents/')
    file_size = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'document'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(employee__isnull=False) | models.Q(site__isnull=False) | models.Q(project__isnull=False),
                name='chk_document_owner_required',
            ),
        ]
        indexes = [
            models.Index(fields=['employee'], name='idx_document_employee'),
            models.Index(fields=['site'], name='idx_document_site'),
            models.Index(fields=['project'], name='idx_document_project'),
            models.Index(fields=['document_type'], name='idx_document_type'),
            models.Index(fields=['created_at'], name='idx_document_created_at'),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Override save to automatically set file_size."""
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    @property
    def file_size_display(self):
        """Return human-readable file size."""
        if self.file_size:
            size = self.file_size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.2f} {unit}"
                size /= 1024
        return 'Unknown'


# Register model for audit logging
auditlog.register(Document)
