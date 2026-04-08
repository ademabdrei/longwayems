"""
Attendance table already has site_id from prior migration cycle.
Sync Django model state with actual DB.
"""
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_convert_site_to_fk'),
        ('attendance', '0001_initial'),
        ('employees', '0003_add_employeesiteassignment_model'),
        ('sites', '0001_initial_site'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(name='attendance', options={'ordering': ['-date', 'employee__first_name']}),
        migrations.AddField(
            model_name='attendance', name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attendances', to='sites.site'),
        ),
        migrations.AddConstraint(
            model_name='attendance',
            constraint=models.UniqueConstraint(fields=('employee', 'date'), name='uq_attendance_employee_date'),
        ),
    ]
