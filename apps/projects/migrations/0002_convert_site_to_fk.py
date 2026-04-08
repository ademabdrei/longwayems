"""
Convert project table from old schema (site varchar, emirate, location, manager)
to new schema (site FK to Site model).

Also recreates employee_project_assignment to maintain FK integrity.
Uses raw SQL because SQLite doesn't support ALTER COLUMN or DROP COLUMN.
"""
from django.db import migrations, models, connection
import django.db.models.deletion


def convert_project_to_site_fk(apps, schema_editor):
    """Convert project and related tables with raw SQL."""
    with connection.cursor() as cursor:
        # ── Phase 1: Save employee_project_assignment data ──
        cursor.execute("ALTER TABLE employee_project_assignment RENAME TO epa_old")

        cursor.execute("""
            CREATE TABLE employee_project_assignment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_date date NOT NULL,
                end_date date NULL,
                status varchar(20) NOT NULL,
                notes text NULL,
                created_at datetime NOT NULL,
                updated_at datetime NOT NULL,
                employee_id bigint NOT NULL REFERENCES "employee" (id) DEFERRABLE INITIALLY DEFERRED,
                project_id bigint NOT NULL REFERENCES "project_old" (id) DEFERRABLE INITIALLY DEFERRED
            )
        """)

        cursor.execute("""
            INSERT INTO employee_project_assignment (id, start_date, end_date, status, notes, created_at, updated_at, employee_id, project_id)
            SELECT id, start_date, end_date, status, notes, created_at, updated_at, employee_id, project_id
            FROM epa_old
        """)

        # ── Phase 2: Recreate project table with site FK ──
        cursor.execute("ALTER TABLE project RENAME TO project_old")

        cursor.execute("""
            CREATE TABLE project (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name varchar(200) NOT NULL,
                site_id bigint NULL REFERENCES "site" (id) DEFERRABLE INITIALLY DEFERRED,
                start_date date NULL,
                end_date date NULL,
                status varchar(20) NOT NULL,
                created_at datetime NOT NULL,
                updated_at datetime NOT NULL
            )
        """)

        # Copy data: map site varchar to site_id via site_name
        cursor.execute("""
            INSERT INTO project (id, project_name, site_id, start_date, end_date, status, created_at, updated_at)
            SELECT po.id, po.project_name, s.id, po.start_date, po.end_date, po.status, po.created_at, po.updated_at
            FROM project_old po
            LEFT JOIN site s ON s.site_name = po.site
        """)

        # ── Phase 3: Re-point employee_project_assignment to new project table ──
        cursor.execute("DROP TABLE epa_old")

        cursor.execute("""
            CREATE TABLE employee_project_assignment_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_date date NOT NULL,
                end_date date NULL,
                status varchar(20) NOT NULL,
                notes text NULL,
                created_at datetime NOT NULL,
                updated_at datetime NOT NULL,
                employee_id bigint NOT NULL REFERENCES "employee" (id) DEFERRABLE INITIALLY DEFERRED,
                project_id bigint NOT NULL REFERENCES "project" (id) DEFERRABLE INITIALLY DEFERRED
            )
        """)

        cursor.execute("""
            INSERT INTO employee_project_assignment_new (id, start_date, end_date, status, notes, created_at, updated_at, employee_id, project_id)
            SELECT id, start_date, end_date, status, notes, created_at, updated_at, employee_id, project_id
            FROM employee_project_assignment
        """)

        cursor.execute("DROP TABLE employee_project_assignment")
        cursor.execute("ALTER TABLE employee_project_assignment_new RENAME TO employee_project_assignment")

        # ── Phase 4: Drop leftover project_old ──
        cursor.execute("DROP TABLE project_old")

        # ── Phase 5: Create indexes ──
        cursor.execute("CREATE INDEX idx_project_status ON project (status)")
        cursor.execute("CREATE INDEX idx_project_site ON project (site_id)")
        cursor.execute("CREATE INDEX idx_project_site_status ON project (site_id, status)")
        cursor.execute("CREATE INDEX employee_project_assignment_employee_id_4555892b ON employee_project_assignment (employee_id)")
        cursor.execute("CREATE INDEX employee_project_assignment_project_id_914dc51c ON employee_project_assignment (project_id)")
        cursor.execute("CREATE UNIQUE INDEX uq_emp_proj_assign_emp_proj_start ON employee_project_assignment (employee_id, project_id, start_date)")
        cursor.execute("CREATE INDEX idx_emp_proj_assign_status ON employee_project_assignment (status)")
        cursor.execute("CREATE INDEX idx_emp_proj_assign_start ON employee_project_assignment (start_date)")
        cursor.execute("CREATE INDEX idx_emp_proj_assign_emp_status ON employee_project_assignment (employee_id, status)")


def reverse_convert(apps, schema_editor):
    """Reverse: restore old project table structure."""
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE employee_project_assignment RENAME TO epa_new")

        cursor.execute("""
            CREATE TABLE employee_project_assignment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_date date NOT NULL,
                end_date date NULL,
                status varchar(20) NOT NULL,
                notes text NULL,
                created_at datetime NOT NULL,
                updated_at datetime NOT NULL,
                employee_id bigint NOT NULL REFERENCES "employee" (id) DEFERRABLE INITIALLY DEFERRED,
                project_id bigint NOT NULL REFERENCES "project" (id) DEFERRABLE INITIALLY DEFERRED
            )
        """)

        cursor.execute("""
            INSERT INTO employee_project_assignment (id, start_date, end_date, status, notes, created_at, updated_at, employee_id, project_id)
            SELECT id, start_date, end_date, status, notes, created_at, updated_at, employee_id, project_id
            FROM epa_new
        """)

        cursor.execute("DROP TABLE epa_new")

        cursor.execute("ALTER TABLE project RENAME TO project_new")

        cursor.execute("""
            CREATE TABLE project (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name varchar(200) NOT NULL,
                site varchar(200) NULL,
                emirate varchar(50) NULL,
                location varchar(300) NULL,
                start_date date NULL,
                end_date date NULL,
                manager_id bigint NULL REFERENCES "custom_user" (id) DEFERRABLE INITIALLY DEFERRED,
                status varchar(20) NOT NULL,
                created_at datetime NOT NULL,
                updated_at datetime NOT NULL
            )
        """)

        cursor.execute("""
            INSERT INTO project (id, project_name, site, emirate, location, start_date, end_date, manager_id, status, created_at, updated_at)
            SELECT pn.id, pn.project_name, s.site_name, NULL, NULL, pn.start_date, pn.end_date, NULL, pn.status, pn.created_at, pn.updated_at
            FROM project_new pn
            LEFT JOIN site s ON s.id = pn.site_id
        """)

        cursor.execute("DROP TABLE project_new")


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ('sites', '0001_initial_site'),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(convert_project_to_site_fk, reverse_convert),
        # State operations so Django knows the actual model structure
        migrations.AlterModelOptions(name='project', options={'ordering': ['-created_at']}),
        migrations.AddField(
            model_name='project', name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='sites.site'),
        ),
        migrations.RemoveField(model_name='project', name='emirate'),
        migrations.RemoveField(model_name='project', name='location'),
        migrations.RemoveField(model_name='project', name='manager'),
        migrations.AddIndex(model_name='project', index=models.Index(fields=['status'], name='idx_project_status')),
        migrations.AddIndex(model_name='project', index=models.Index(fields=['site'], name='idx_project_site')),
        migrations.AddIndex(model_name='project', index=models.Index(fields=['site', 'status'], name='idx_project_site_status')),
        migrations.AlterField(
            model_name='employeeprojectassignment', name='employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_assignments', to='employees.employee'),
        ),
        migrations.AlterField(
            model_name='employeeprojectassignment', name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_assignments', to='projects.project'),
        ),
        migrations.AddIndex(model_name='employeeprojectassignment', index=models.Index(fields=['status'], name='idx_emp_proj_assign_status')),
        migrations.AddIndex(model_name='employeeprojectassignment', index=models.Index(fields=['start_date'], name='idx_emp_proj_assign_start')),
        migrations.AddIndex(model_name='employeeprojectassignment', index=models.Index(fields=['employee', 'status'], name='idx_emp_proj_assign_emp_status')),
        migrations.AddConstraint(
            model_name='employeeprojectassignment',
            constraint=models.UniqueConstraint(fields=('employee', 'project', 'start_date'), name='uq_emp_proj_assignment_emp_proj_start'),
        ),
    ]
