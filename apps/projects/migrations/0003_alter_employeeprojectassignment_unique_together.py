"""
Sync state: EmployeeProjectAssignment no longer has unique_together.
Already replaced by UniqueConstraint in 0002. Only update Django's state.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_convert_site_to_fk'),
    ]

    operations = [
        migrations.AlterUniqueTogether(name='employeeprojectassignment', unique_together=set()),
    ]
