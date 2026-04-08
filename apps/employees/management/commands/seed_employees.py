"""
Management command to seed employees and their site assignment history.
"""
import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand

from apps.employees.models import Employee, EmployeeSiteAssignment
from apps.sites.models import Site
from apps.projects.models import Project, EmployeeProjectAssignment


class Command(BaseCommand):
    help = 'Seed 35+ employees with site assignment history and project assignments'

    FIRST_NAMES = [
        'Mohammed', 'Ahmed', 'Ali', 'Omar', 'Hassan', 'Ibrahim', 'Yusuf',
        'Khalid', 'Saeed', 'Rashid', 'Hamdan', 'Mansour', 'Sultan', 'Faisal',
        'Tariq', 'Nasser', 'Abdullah', 'Salim', 'Majid', 'Farid', 'Zayed',
        'Jaber', 'Salem', 'Waleed', 'Amir', 'Karim', 'Mustafa', 'Samir',
        'Hisham', 'Bilal', 'Rami', 'Tamer', 'Emad', 'Adel', 'Hani',
        'Layla', 'Fatima', 'Aisha', 'Maryam', 'Noor', 'Sara', 'Huda',
        'Rania', 'Mona', 'Dina', 'Yasmin', 'Lina', 'Rana',
    ]

    LAST_NAMES = [
        'Al Mansouri', 'Al Hashimi', 'Al Maktoum', 'Al Qasimi', 'Al Nuaimi',
        'Al Ketbi', 'Al Mazrouei', 'Al Dhaheri', 'Al Shamsi', 'Al Kaabi',
        'Al Marri', 'Al Muhairi', 'Al Suwaidi', 'Al Hammadi', 'Al Blooshi',
        'Al Falasi', 'Al Naqbi', 'Al Rumaithi', 'Al Shamsi', 'Al Kindi',
    ]

    POSITIONS = [
        'Site Supervisor', 'Welder', 'Electrician', 'Plumber', 'Mason',
        'Painter', 'Carpenter', 'HVAC Technician', 'Cleaner', 'Security Guard',
        'Heavy Equipment Operator', 'Steel Fixer', 'Tile Setter', 'Helper',
        'Foreman', 'Safety Officer', 'Store Keeper', 'Driver',
    ]

    NATIONALITIES = [
        'Emirati', 'Indian', 'Pakistani', 'Bangladeshi', 'Egyptian',
        'Filipino', 'Sri Lankan', 'Nepalese', 'Jordanian', 'Sudanese',
    ]

    NOTES_POOL = [
        'Assigned for phase 1 construction.',
        'Transferred from another site.',
        'Promoted to senior role.',
        'Temporary assignment during peak season.',
        'Reassigned after site completion.',
        'Covering for absent staff.',
        'Specialized skill requirement.',
        'Contract renewal pending.',
        'Performance review scheduled.',
        'Completed training certification.',
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--count', type=int, default=35,
            help='Number of employees to create (default: 35)',
        )

    def handle(self, *args, **options):
        count = options['count']
        sites = list(Site.objects.all())
        projects = list(Project.objects.all())

        if not sites:
            self.stdout.write(self.style.ERROR('No sites found. Create at least one site first.'))
            return

        self.stdout.write(f'Found {len(sites)} site(s): {", ".join(s.site_name for s in sites)}')

        existing_emails = set(Employee.objects.values_list('email', flat=True).exclude(email__isnull=True))
        created_employees = []
        skipped = 0

        for i in range(count):
            first_name = random.choice(self.FIRST_NAMES)
            last_name = random.choice(self.LAST_NAMES)
            position = random.choice(self.POSITIONS)
            nationality = random.choice(self.NATIONALITIES)
            gender = 'Male' if first_name not in ('Layla', 'Fatima', 'Aisha', 'Maryam', 'Noor', 'Sara', 'Huda', 'Rania', 'Mona', 'Dina', 'Yasmin', 'Lina', 'Rana') else 'Female'

            # Generate unique email
            base_email = f'{first_name.lower()}.{last_name.lower().replace(" ", "")}@company.com'
            email = base_email
            counter = 1
            while email in existing_emails:
                email = f'{first_name.lower()}.{last_name.lower().replace(" ", "")}{counter}@company.com'
                counter += 1
            existing_emails.add(email)

            hire_date = date(2023, 1, 1) + timedelta(days=random.randint(0, 700))
            basic_salary = random.choice([1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 6000, 7000, 8000, 10000, 12000])

            employee = Employee.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=f'+971-50-{random.randint(1000000, 9999999):07d}',
                gender=gender,
                nationality=nationality,
                position=position,
                basic_salary=basic_salary,
                hire_date=hire_date,
                status='Active',
            )
            created_employees.append(employee)

        self.stdout.write(self.style.SUCCESS(f'Created {len(created_employees)} employees.'))

        # Create site assignment history
        total_site_assignments = 0
        for employee in created_employees:
            num_assignments = random.choices([1, 2, 3], weights=[50, 35, 15])[0]
            assignment_start = employee.hire_date

            for j in range(num_assignments):
                site = random.choice(sites)
                start = assignment_start + timedelta(days=random.randint(0, 30))

                if j < num_assignments - 1:
                    end = start + timedelta(days=random.randint(60, 365))
                    status = random.choice(['Completed', 'Completed', 'Terminated', 'On Hold'])
                    notes = random.choice(self.NOTES_POOL) if random.random() > 0.4 else ''
                else:
                    end = None
                    status = 'Active'
                    notes = random.choice(self.NOTES_POOL) if random.random() > 0.5 else ''

                # Avoid duplicate
                existing = EmployeeSiteAssignment.objects.filter(
                    employee=employee, site=site, start_date=start
                ).first()
                if existing:
                    start += timedelta(days=1)

                EmployeeSiteAssignment.objects.create(
                    employee=employee,
                    site=site,
                    start_date=start,
                    end_date=end,
                    status=status,
                    notes=notes,
                )
                total_site_assignments += 1
                assignment_start = (end or date.today()) + timedelta(days=1)

        self.stdout.write(self.style.SUCCESS(f'Created {total_site_assignments} site assignment(s).'))

        # Create project assignments within sites
        total_project_assignments = 0
        for employee in created_employees:
            site_assignment = employee.current_site_assignment
            if site_assignment and projects:
                # Assign to 1-2 projects within the assigned site
                site_projects = [p for p in projects if p.site_id == site_assignment.site_id]
                if not site_projects:
                    site_projects = projects[:1]
                num_proj = random.choice([1, 2])
                for proj in random.sample(site_projects, min(num_proj, len(site_projects))):
                    EmployeeProjectAssignment.objects.create(
                        employee=employee,
                        project=proj,
                        start_date=site_assignment.start_date,
                        status=site_assignment.status,
                    )
                    total_project_assignments += 1

        # Summary
        active_site = EmployeeSiteAssignment.objects.filter(status='Active').count()
        completed_site = EmployeeSiteAssignment.objects.filter(status='Completed').count()
        self.stdout.write(self.style.SUCCESS(
            f'\nSummary: {Employee.objects.count()} total employees, '
            f'{total_site_assignments} site assignments ({active_site} active, {completed_site} completed).'
        ))
