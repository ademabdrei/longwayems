# Employee Management System (EMS)

A comprehensive Django-based Employee Management System designed for construction and field-based companies operating in the UAE. This system manages employees, projects, attendance, payroll, timesheets, and documents with role-based access control.

## Features

- **User Authentication & Authorization**: Session-based authentication with three roles (Admin, Manager, Employee)
- **Employee Management**: Complete CRUD operations for employee profiles
- **Project Management**: Track projects with employee assignments
- **Attendance Tracking**: Daily attendance marking with overtime support
- **Timesheets**: Multi-project daily timesheet entries
- **Payroll Management**: Automated payroll generation with overtime calculations
- **Document Management**: File uploads and management per employee/project
- **Audit Trail**: Full audit logging using django-auditlog
- **Export Functionality**: Excel and PDF exports for reports and payslips
- **Responsive UI**: Bootstrap 5-based responsive design

## Tech Stack

- **Backend**: Django 4.2+ (Pure Django, NO Django REST Framework)
- **Frontend**: Django HTML Templates + Bootstrap 5
- **Database**: SQLite (default for local development)
- **Authentication**: Django built-in session-based authentication
- **Admin**: Heavily customized Django Admin Panel
- **Audit Trail**: django-auditlog
- **File Storage**: Local media folder
- **Exports**: Excel (openpyxl) + PDF (reportlab)

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git (for cloning the repository)

## Installation & Setup

### 1. Clone the Repository

```bash
cd G:\Python\Django\LongwayEMS
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run Database Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account. Remember your credentials!

### 7. Run the Development Server

```bash
python manage.py runserver
```

The application will be available at: `http://127.0.0.1:8000/`

## Default Login Credentials

After creating a superuser, you can log in with those credentials. To create additional users:

1. Log in as Admin
2. Navigate to **User Management** in the sidebar
3. Click **Add User** to create new Admin, Manager, or Employee accounts

## Folder Structure

```
LongwayEMS/
│
├── config/                  # Main Django project settings
│   ├── __init__.py
│   ├── settings.py          # Django settings configuration
│   ├── urls.py              # Main URL routing
│   └── wsgi.py              # WSGI application
│
├── apps/                    # Django applications
│   ├── accounts/            # User auth, login, roles
│   ├── employees/           # Employee CRUD, profile
│   ├── projects/            # Project CRUD, assignments
│   ├── attendance/          # Daily attendance marking
│   ├── timesheets/          # Multi-project daily timesheets
│   ├── payroll/             # Salary, overtime, payslips
│   └── documents/           # File uploads per employee/project
│
├── templates/               # Global templates folder
│   ├── base.html            # Base template with sidebar
│   ├── accounts/            # Account-related templates
│   ├── employees/           # Employee templates
│   ├── projects/            # Project templates
│   ├── attendance/          # Attendance templates
│   ├── timesheets/          # Timesheet templates
│   ├── payroll/             # Payroll templates
│   └── documents/           # Document templates
│
├── static/                  # CSS, JS, images
├── media/                   # Uploaded files (gitignored)
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Module Descriptions

### Accounts Module
- User login/logout
- Dashboard with role-aware statistics
- Profile management
- Password change
- User management (Admin only)
- Activity log viewing (Admin only)

### Employees Module
- Employee list with search and filters
- Create, edit, view, and deactivate employees
- Export employee data to Excel
- View project assignments and attendance summary

### Projects Module
- Project list with status and emirate filters
- Create, edit, and delete projects
- Assign employees to projects
- View project details and attendance stats

### Attendance Module
- Daily attendance records with filters
- Bulk attendance marking for projects
- Edit individual attendance records
- Monthly attendance summary
- Export to Excel or PDF

### Timesheets Module
- Timesheet list with filters
- Create and edit timesheets
- Export timesheets to Excel

### Payroll Module
- Payroll list with month/year filters
- Auto-generate payroll from attendance data
- View detailed payslip information
- Download PDF payslips
- Export payroll data to Excel

### Documents Module
- Document list with type filters
- Upload documents with metadata
- View and download documents
- Edit document metadata
- Delete documents (removes file from disk)

## Role-Based Access Control

### Admin
- Full access to ALL modules
- Can create/edit/delete users, employees, projects
- Can process payroll and mark attendance
- Can view all reports and export data
- Can access Django Admin panel (`/admin/`)

### Manager
- Can view/edit employees assigned to their projects
- Can mark and edit attendance for their project's employees
- Can view timesheets and payroll summaries
- Can upload and view documents
- **Cannot** delete employees or process payroll
- **Cannot** access Django Admin panel

### Employee
- Can only view their own profile
- Can view their own attendance history
- Can view their own payroll/payslip
- Can view their own documents
- **Cannot** edit any data
- **Cannot** access Django Admin panel

## How to Create the First Admin User

1. Run the development server: `python manage.py runserver`
2. Navigate to: `http://127.0.0.1:8000/admin/`
3. Click "Add" next to "Users" under "AUTHENTICATION AND AUTHORIZATION"
4. Fill in the required fields:
   - Username
   - Password (and confirmation)
   - First Name, Last Name
   - Email
   - Role: Select "Admin"
   - Check "Staff status" and "Superuser status"
5. Click "Save"

Alternatively, use the command line:
```bash
python manage.py createsuperuser
```

## How to Run Exports

### Excel Exports
1. Navigate to the respective module (Employees, Attendance, Timesheets, Payroll)
2. Click the "Export" button (visible to Admin/Manager roles)
3. The file will download automatically with the format: `module_YYYY-MM-DD.xlsx`

### PDF Exports
1. **Payslip PDF**: Navigate to Payroll → View a payroll record → Click "Download Payslip PDF"
2. **Attendance PDF**: Navigate to Attendance → Summary → Select month/year → Click "Export PDF"

## Overtime Calculation Formula

The system calculates overtime pay using the following formula:

```
Overtime Pay = (Basic Salary / 30 / 8) × 1.5 × Overtime Hours
```

Where:
- `Basic Salary / 30` = Daily rate
- `Daily Rate / 8` = Hourly rate
- `Hourly Rate × 1.5` = Overtime hourly rate (1.5x normal rate)
- `Overtime Hourly Rate × Overtime Hours` = Total overtime pay

## Net Salary Calculation

```
Net Salary = Basic Salary + Allowances + Overtime Pay - Deductions
```

## Audit Trail

All changes to the following models are logged:
- CustomUser
- Employee
- Project
- EmployeeProjectAssignment
- Attendance
- Timesheet
- Payroll
- Document

View the audit log at: **User Management → Activity Log** (Admin only)

## Support

For issues or questions, please contact your system administrator.

---

**© 2024 Employee Management System. All rights reserved.**
