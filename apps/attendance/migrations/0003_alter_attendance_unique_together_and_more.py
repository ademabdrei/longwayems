"""
Sync state: attendance no longer has 'project' field or unique_together.
Already removed by raw SQL. Only update Django's state.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0002_convert_project_to_site'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AlterUniqueTogether(name='attendance', unique_together=set()),
                migrations.RemoveField(model_name='attendance', name='project'),
            ],
        ),
    ]
