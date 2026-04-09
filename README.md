# Employee Management System (EMS)

A comprehensive Django-based Employee Management System designed for construction and field-based companies operating in the UAE. This system manages employees, sites, projects, attendance, payroll, timesheets, and documents with role-based access control and a modern, AJAX-powered user interface.

## 🌟 Overview

LongwayEMS is a full-featured enterprise application built with Django and Bootstrap 5. It provides a complete solution for managing field employees across multiple sites and projects, with advanced attendance tracking, payroll calculation, timesheet management, and document handling. The system features a modern AJAX-based modal interface, eliminating page reloads for most operations.

**Current Status**: 
- ✅ **Complete & Production-Ready**: Accounts, Employees, Sites, Projects, Attendance
- 🚧 **Models Ready, Views Pending**: Timesheets, Payroll, Documents

---

## 📋 Table of Contents

- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Module Details](#-module-details)
- [Database Models](#-database-models)
- [URL Routing](#-url-routing)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Usage Guide](#-usage-guide)
- [Role-Based Access](#-role-based-access-control)
- [Management Commands](#-management-commands)
- [Export Functionality](#-export-functionality)
- [Audit Trail](#-audit-trail)
- [Folder Structure](#-folder-structure)
- [Support](#-support)

---

## ✨ Key Features

### Core Features
- **Session-Based Authentication**: Secure login/logout with Django's built-in authentication system
- **Role-Based Access Control**: Three-tier roles (Admin, Manager, Employee)
- **AJAX-Powered Modals**: Create, edit, and delete records without page reloads
- **Site-Based Organization**: Organize employees and projects by physical sites/locations
- **UAE-Specific**: Supports all 7 UAE emirates (Abu Dhabi, Dubai, Sharjah, Ajman, Umm Al Quwain, Ras Al Khaimah, Fujairah)
- **Responsive Design**: Bootstrap 5-based mobile-friendly interface
- **Audit Logging**: Complete change history for all models using django-auditlog

### Advanced Attendance System
- **Inline Status Dropdowns**: Change attendance directly from table rows with color-coded badges
- **Bulk Update Toolbar**: Select multiple employees and update status, overtime, or notes simultaneously
- **Smart Partial Updates**: Only modifies fields you fill in - existing values are preserved
- **Project Tracking**: Assign employees to specific projects when marking attendance
- **Date Navigation**: Quick previous/next day buttons with "Today" shortcut
- **Statistics Dashboard**: Real-time cards showing Total, Present, Absent, Night, Double, Half, On Leave, Unmarked counts
- **Toast Notifications**: Centered, animated notifications with detailed update information
- **Auto-Refresh**: Page automatically refreshes after any update to show fresh data

### Employee & Assignment Management
- **Employee CRUD**: Complete create, read, update, delete with modal dialogs
- **Site Assignments**: Assign employees to sites with date tracking and automatic closure of previous assignments
- **Project Assignments**: Assign employees to specific projects within their assigned site
- **Assignment History**: View complete site and project assignment history per employee
- **Smart Filtering**: Search by name, filter by status (Active/Inactive), gender, and site
- **Unassigned Employees**: Quick view of employees not currently assigned to any site
- **Profile Pictures**: Support for employee profile photos with avatar fallbacks

### Site & Project Management
- **Site CRUD via Modals**: Create, edit, view details, and delete sites without page reloads
- **Manager Assignment**: Assign system users as site managers
- **Duration Tracking**: Automatic calculation of site/project duration
- **Status Management**: Track sites and projects through lifecycle (Pending → Active → Completed)
- **Emirate Filtering**: Filter sites by UAE emirate
- **Active Counts**: Real-time counts of active projects and employees per site

### Dashboard & Reporting
- **Admin Dashboard**: Centralized view with statistics cards and quick actions
- **Quick Actions**: One-click access to common tasks (Add Employee, New Project, Assign Employee)
- **Recent Activity**: Lists of recently added employees, projects, and assignments
- **Statistics Aggregation**: Cross-module statistics on dashboard

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Browser                              │
│              (Bootstrap 5 + Vanilla JS)                      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP Requests
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Django Server                              │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Accounts │  │Employees │  │  Sites   │  │ Projects │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Attendance│  │Timesheets│  │  Payroll │  │Documents │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Service Layer (AssignmentService)           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         django-auditlog (Change Tracking)            │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  SQLite Database                              │
│  (custom_user, employee, site, project, attendance, ...)    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Module Details

### 1. Accounts Module ✅ Complete

**Purpose**: User authentication, authorization, and system user management.

**Features**:
- Login/logout with session-based authentication
- Admin-only login (currently restricted to Admin role)
- Admin dashboard with aggregated statistics
- User management (create, edit, delete system users)
- Role assignment (Admin, Manager, Employee)
- Profile management with profile pictures

**Views**:
- `login_view` - Session-based login
- `logout_view` - Logout and redirect
- `admin_dashboard_view` - Dashboard with stats
- `user_list` - List users with filters
- `user_create` - Create new user with password hashing
- `user_update` - Update existing user
- `user_delete` - Delete user

**URLs**: `/accounts/login/`, `/accounts/logout/`, `/accounts/dashboard/`, `/accounts/users/`

---

### 2. Employees Module ✅ Complete

**Purpose**: Manage employee profiles, site assignments, and project assignments.

**Features**:
- Employee list with search and filters
- Create, edit, view, and deactivate employees
- Modal-based CRUD operations (no page reloads)
- Site assignment with automatic closure of previous assignments
- Project assignment within assigned sites
- Assignment history tracking
- Unassigned employees quick view
- Export to Excel (planned)

**Models**:
- `Employee` - Employee profile with personal and employment data
- `EmployeeSiteAssignment` - Links employees to sites with date tracking

**Views**: 14 views including list, CRUD, modals, and assignment endpoints

**URLs**: 19 URL patterns covering all operations

**Management Command**: `seed_employees` - Generate test data

---

### 3. Sites Module ✅ Complete

**Purpose**: Manage physical locations/sites where employees work.

**Features**:
- Site list with emirate and status filters
- Modal-based CRUD operations
- Site manager assignment
- Active project and employee counts
- Duration calculation from start/end dates
- Sidebar navigation in other modules

**Model**: `Site` - Site with name, emirate, location, manager, status, dates

**Views**: 5 modal-based views (create, update, detail, delete)

**URLs**: 5 URL patterns

---

### 4. Projects Module ✅ Complete

**Purpose**: Manage projects within sites and assign employees to them.

**Features**:
- Project list with site sidebar navigation
- Status and search filters
- Modal-based CRUD operations
- Employee assignment to projects
- Active employee counts
- Duration tracking

**Models**:
- `Project` - Project within a site
- `EmployeeProjectAssignment` - Links employees to projects

**Views**: 5 modal-based views

**URLs**: 6 URL patterns

---

### 5. Attendance Module ✅ Complete (Most Advanced)

**Purpose**: Track daily employee attendance, overtime, and notes.

**Features**:
- **Date-Based Management**: Select any date and manage attendance for that day
- **Site Sidebar**: Filter employees by site with employee counts
- **Statistics Cards**: Real-time counts for each attendance status
- **Inline Dropdowns**: Change status directly from table rows
- **Color-Coded Badges**: Visual status indicators (green=Present, red=Absent, etc.)
- **Bulk Update Toolbar**:
  - Checkbox selection (individual or select all)
  - Status dropdown (optional)
  - Overtime hours input (optional)
  - Notes input (optional)
  - Apply button for all selected
  - Clear selection button
- **Smart Partial Updates**: Only updates fields you fill in
- **Project Assignment**: Track which project an employee worked on
- **Date Navigation**: Previous day, Today, Next day buttons
- **Save All Changes**: Save all individual dropdown changes in parallel
- **AJAX-Powered**: All operations without full page reloads
- **Toast Notifications**: Beautiful centered notifications with details
- **Auto-Refresh**: Page refreshes after updates for fresh data

**Model**: `Attendance` - Daily attendance with status, overtime, notes, project

**Views**: 17 views including quick attendance, bulk update, and modals

**URLs**: 20 URL patterns including AJAX endpoints

**Attendance Status Options**:
- Unmarked
- Present
- Night
- Double
- Half
- Absent
- On Leave

---

### 6. Timesheets Module 🚧 Model Ready

**Purpose**: Track daily work hours across multiple projects.

**Current Status**: Model created with fields, views and URLs pending implementation.

**Model**: `Timesheet` - Employee, site, project, date, task description, notes

**Planned Features**:
- Daily timesheet entry per employee
- Multi-project time tracking
- Task description and notes
- Export to Excel

---

### 7. Payroll Module 🚧 Model Ready

**Purpose**: Calculate and manage employee payroll with overtime.

**Current Status**: Model created with calculation logic, views and URLs pending implementation.

**Model**: `Payroll` - Employee, month, year, salary components, overtime calculation

**Built-in Calculations**:
- `calculate_overtime_pay()` - Formula: `(basic_salary / 30 / 8) × 1.5 × overtime_hours`
- `calculate_net_salary()` - Formula: `basic + allowances + overtime_pay - deductions`
- Auto-calculation on save

**Planned Features**:
- Monthly payroll generation
- Overtime auto-calculation from attendance
- Allowances and deductions
- PDF payslip generation
- Export to Excel

---

### 8. Documents Module 🚧 Model Ready

**Purpose**: Manage employee and project-related documents.

**Current Status**: Model created with file upload support, views and URLs pending implementation.

**Model**: `Document` - Employee/site/project linkage, document type, file upload, auto file size

**Planned Features**:
- Document upload with metadata
- File type and size tracking
- Link to employee, site, or project
- Download and view documents
- Document type categorization

---

## 🗄 Database Models

### Accounts
| Model | Table | Description |
|-------|-------|-------------|
| `CustomUser` | `custom_user` | Extends Django User with role (Admin/Manager/Employee), phone, profile picture |

### Employees
| Model | Table | Description |
|-------|-------|-------------|
| `Employee` | `employee` | Employee profile: name, email, phone, gender, nationality, position, salary, hire date, status |
| `EmployeeSiteAssignment` | `employee_site_assignment` | Links employee to site with start/end dates, status, notes. Custom manager with query helpers. |

### Sites
| Model | Table | Description |
|-------|-------|-------------|
| `Site` | `site` | Physical location: name, emirate (7 UAE options), location, manager, status, dates, notes |

### Projects
| Model | Table | Description |
|-------|-------|-------------|
| `Project` | `project` | Work project within a site: name, site FK, dates, status |
| `EmployeeProjectAssignment` | `employee_project_assignment` | Links employee to project with dates, status, notes |

### Attendance
| Model | Table | Description |
|-------|-------|-------------|
| `Attendance` | `attendance` | Daily attendance: employee, site, project, date, status (7 options), overtime hours, notes, created_by |

### Timesheets
| Model | Table | Description |
|-------|-------|-------------|
| `Timesheet` | `timesheet` | Work log: employee, site, project, date, task description, notes |

### Payroll
| Model | Table | Description |
|-------|-------|-------------|
| `Payroll` | `payroll` | Monthly payroll: employee, month, year, basic salary, allowances, deductions, overtime, net salary (auto-calculated) |

### Documents
| Model | Table | Description |
|-------|-------|-------------|
| `Document` | `document` | File storage: employee/site/project FKs, document type, title, file upload, auto file_size |

---

## 🌐 URL Routing

### Main URLs (config/urls.py)
| URL Pattern | App | Description |
|-------------|-----|-------------|
| `/` | Root | Redirects to dashboard |
| `/admin/` | Django Admin | Default Django admin |
| `/accounts/` | Accounts | Authentication & user management |
| `/employees/` | Employees | Employee management |
| `/sites/` | Sites | Site management |
| `/projects/` | Projects | Project management |
| `/attendance/` | Attendance | Attendance tracking |
| `/timesheets/` | Timesheets | Timesheets (stub) |
| `/payroll/` | Payroll | Payroll (stub) |
| `/documents/` | Documents | Documents (stub) |

### Detailed URL Patterns

**Accounts** (7 patterns):
- `/accounts/login/` - Login page
- `/accounts/logout/` - Logout
- `/accounts/dashboard/` - Admin dashboard
- `/accounts/users/` - User list
- `/accounts/users/create/` - Create user
- `/accounts/users/<pk>/update/` - Update user
- `/accounts/users/<pk>/delete/` - Delete user

**Employees** (19 patterns):
- `/employees/` - Employee list
- `/employees/site/<site_pk>/` - Employees by site
- `/employees/unassigned/` - Unassigned employees
- `/employees/create/` - Create employee
- `/employees/<pk>/` - Employee detail
- `/employees/<pk>/update/` - Update employee
- `/employees/<pk>/delete/` - Delete employee
- `/employees/modal/create/` - Create modal (AJAX)
- `/employees/modal/<pk>/update/` - Update modal (AJAX)
- `/employees/modal/<pk>/delete/` - Delete modal (AJAX)
- `/employees/modal/<pk>/site-history/` - Site assignment history modal
- `/employees/<pk>/site-assignment/` - Assign to site
- `/employees/<pk>/site-assignment/end/` - End site assignment
- Plus legacy assignment endpoints

**Sites** (5 patterns):
- `/sites/` - Site list
- `/sites/modal/create/` - Create modal (AJAX)
- `/sites/modal/<pk>/update/` - Update modal (AJAX)
- `/sites/modal/<pk>/detail/` - Detail modal
- `/sites/modal/<pk>/delete/` - Delete modal (AJAX)

**Projects** (6 patterns):
- `/projects/` - Project list
- `/projects/site/<site_pk>/` - Projects by site
- `/projects/modal/create/` - Create modal (AJAX)
- `/projects/modal/<pk>/update/` - Update modal (AJAX)
- `/projects/modal/<pk>/detail/` - Detail modal
- `/projects/modal/<pk>/delete/` - Delete modal (AJAX)

**Attendance** (20 patterns):
- `/attendance/` - Attendance list
- `/attendance/site/<site_pk>/` - Attendance by site
- `/attendance/site/<site_pk>/quick/` - Quick attendance for site
- `/attendance/site/<site_pk>/bulk-mark/` - Bulk mark for site
- `/attendance/create/` - Create attendance
- `/attendance/<pk>/update/` - Update attendance
- `/attendance/<pk>/delete/` - Delete attendance
- `/attendance/bulk/` - Bulk attendance form
- `/attendance/modal/create/` - Create modal (AJAX)
- `/attendance/modal/<pk>/update/` - Update modal (AJAX)
- `/attendance/modal/<pk>/delete/` - Delete modal (AJAX)
- `/attendance/ajax/quick-mark/` - Quick mark (AJAX)
- `/attendance/ajax/quick-update/` - Quick update (AJAX)
- `/attendance/ajax/quick-delete/<pk>/` - Quick delete (AJAX)
- `/attendance/ajax/bulk-update/` - Bulk update (AJAX)

---

## 🛠 Tech Stack

| Category | Technology |
|----------|------------|
| **Backend Framework** | Django 4.2+ (Pure Django, NO Django REST Framework) |
| **Frontend** | Django HTML Templates + Bootstrap 5 + Bootstrap Icons |
| **JavaScript** | Vanilla JavaScript (no frameworks, inline in templates) |
| **Database** | SQLite (default, switchable to PostgreSQL/MySQL) |
| **Authentication** | Django built-in session-based authentication |
| **Admin Panel** | Default Django Admin (not customized) |
| **Audit Trail** | django-auditlog 2.3+ |
| **Forms** | django-crispy-forms 2.0+ with Bootstrap 5 |
| **Image Processing** | Pillow 10.0+ |
| **Excel Export** | openpyxl 3.1+ (planned) |
| **PDF Export** | reportlab 4.0+ (planned) |
| **HTTP Requests** | Fetch API for AJAX calls |

---

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Git

### Step-by-Step Setup

**1. Clone the Repository**
```bash
git clone https://github.com/ademabdrei/longwayems.git
cd longwayems
```

**2. Create Virtual Environment**
```bash
python -m venv venv
```

**3. Activate Virtual Environment**
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

**4. Install Dependencies**
```bash
pip install -r requirements.txt
```

**5. Run Database Migrations**
```bash
python manage.py migrate
```

**6. Create Superuser (Admin)**
```bash
python manage.py createsuperuser
```

**7. (Optional) Seed Test Data**
```bash
python manage.py seed_employees --count 50
```

**8. Run Development Server**
```bash
python manage.py runserver
```

Access the application at: `http://127.0.0.1:8000/`

---

## 📖 Usage Guide

### First-Time Setup

1. **Create Admin User**:
   ```bash
   python manage.py createsuperuser
   ```

2. **Login**:
   - Navigate to `http://127.0.0.1:8000/accounts/login/`
   - Enter admin credentials
   - Currently only Admin role can login

3. **Create Sites**:
   - Go to Sites from navigation
   - Click "New Site"
   - Fill in site name, emirate, location, manager

4. **Create Employees**:
   - Go to Employees
   - Click "New Employee"
   - Fill in employee details
   - Assign to a site

5. **Mark Attendance**:
   - Go to Attendance
   - Select employees via checkboxes
   - Use inline dropdownes or bulk update toolbar
   - Click "Save All Changes" or "Apply"

### Daily Workflow

1. **Mark Attendance**:
   - Navigate to Attendance
   - Use date navigation if needed
   - Select employees and update status via dropdowns
   - Or use bulk update for multiple employees
   - Add overtime hours and notes as needed

2. **Manage Employees**:
   - Add new employees via modal
   - Assign to sites/projects
   - View assignment history

3. **Monitor Sites & Projects**:
   - View site sidebar in employees/attendance
   - Check active counts
   - Filter by emirate or status

---

## 👥 Role-Based Access Control

### Current Implementation

**Important**: Currently, only **Admin** users can log in. The login view explicitly checks `if user.role != 'Admin'` and blocks other roles. Manager and Employee roles exist in the model but their access is not yet implemented.

| Permission | Admin | Manager | Employee |
|------------|-------|---------|----------|
| Login | ✅ Yes | ❌ Blocked | ❌ Blocked |
| View Dashboard | ✅ Yes | ❌ | ❌ |
| Manage Users | ✅ Yes | ❌ | ❌ |
| Employee CRUD | ✅ Yes | ❌ | ❌ |
| Site CRUD | ✅ Yes | ❌ | ❌ |
| Project CRUD | ✅ Yes | ❌ | ❌ |
| Attendance | ✅ Yes | ❌ | ❌ |
| Access Django Admin | ✅ Yes | ❌ | ❌ |

### Planned Role Permissions

| Permission | Admin | Manager | Employee |
|------------|-------|---------|----------|
| Full system access | ✅ | Partial | View only |
| Manage employees | ✅ | Assigned only | Self only |
| Manage sites | ✅ | Assigned sites | ❌ |
| Mark attendance | ✅ | Assigned employees | Self only |
| Process payroll | ✅ | ❌ | ❌ |
| View reports | ✅ | Assigned scope | Self only |
| Access Django Admin | ✅ | ❌ | ❌ |

---

## 🔧 Management Commands

### seed_employees

Generates test employee data with realistic site and project assignments.

**Usage**:
```bash
# Generate 35 employees (default)
python manage.py seed_employees

# Generate 100 employees
python manage.py seed_employees --count 100
```

**Requirements**: At least one Site must exist before running.

**What it creates**:
- Employees with randomized names, emails, phone numbers
- Random nationalities, genders, positions, salaries
- Site assignment history (1-3 assignments per employee)
- Project assignments within assigned sites
- Realistic dates spanning the past year

---

## 📤 Export Functionality

**Current Status**: Export libraries are installed (`openpyxl`, `reportlab`) but export views are not yet implemented.

### Planned Exports

**Excel Exports** (`.xlsx`):
- Employee list
- Attendance records
- Timesheets
- Payroll data

**PDF Exports**:
- Payslips (per payroll record)
- Attendance summary reports (by month/year)

### Usage (When Implemented)

1. Navigate to the respective module
2. Click the "Export" button (Admin/Manager roles)
3. File downloads automatically with format: `module_YYYY-MM-DD.xlsx`

---

## 🔍 Audit Trail

All model changes are automatically logged using `django-auditlog`.

### Tracked Models
- CustomUser
- Employee
- EmployeeSiteAssignment
- Site
- Project
- EmployeeProjectAssignment
- Attendance
- Timesheet
- Payroll
- Document

### What's Logged
- Create operations
- Update operations (with before/after values)
- Delete operations
- User who made the change
- Timestamp
- IP address

### Viewing Audit Log
Currently accessible via Django Admin at `/admin/auditlog/`. A user-friendly view is planned for the User Management module.

---

## 📁 Folder Structure

```
LongwayEMS/
│
├── config/                          # Main Django project configuration
│   ├── __init__.py
│   ├── settings.py                  # Django settings (DB, apps, middleware, static/media)
│   ├── urls.py                      # Main URL routing
│   └── wsgi.py                      # WSGI application for deployment
│
├── apps/                            # Django applications (8 apps)
│   ├── __init__.py
│   │
│   ├── accounts/                    # User authentication & management
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── models.py                # CustomUser model
│   │   ├── views.py                 # Login, logout, dashboard, user CRUD
│   │   ├── urls.py
│   │   ├── forms.py
│   │   └── admin.py
│   │
│   ├── employees/                   # Employee management & assignments
│   │   ├── migrations/
│   │   ├── management/commands/
│   │   │   └── seed_employees.py    # Test data generation
│   │   ├── __init__.py
│   │   ├── models.py                # Employee, EmployeeSiteAssignment
│   │   ├── views.py                 # Employee CRUD, modals, assignments
│   │   ├── urls.py
│   │   ├── forms.py
│   │   └── admin.py
│   │
│   ├── sites/                       # Site/location management
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── models.py                # Site model
│   │   ├── views.py                 # Site CRUD via modals
│   │   ├── urls.py
│   │   ├── forms.py
│   │   └── admin.py
│   │
│   ├── projects/                    # Project management & assignments
│   │   ├── migrations/
│   │   ├── services.py              # AssignmentService
│   │   ├── __init__.py
│   │   ├── models.py                # Project, EmployeeProjectAssignment
│   │   ├── views.py                 # Project CRUD via modals
│   │   ├── urls.py
│   │   ├── forms.py
│   │   └── admin.py
│   │
│   ├── attendance/                  # Daily attendance tracking
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── models.py                # Attendance model
│   │   ├── views.py                 # Attendance list, bulk update, AJAX endpoints
│   │   ├── urls.py
│   │   ├── forms.py
│   │   └── admin.py
│   │
│   ├── timesheets/                  # Timesheet management (stub)
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   └── models.py                # Timesheet model
│   │
│   ├── payroll/                     # Payroll management (stub)
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   └── models.py                # Payroll model with calculations
│   │
│   └── documents/                   # Document management (stub)
│       ├── migrations/
│       ├── __init__.py
│       └── models.py                # Document model
│
├── templates/                       # Django HTML templates
│   ├── base.html                    # Base template with Bootstrap 5
│   ├── _header.html                 # Top navigation bar
│   │
│   ├── accounts/                    # Account templates
│   │   ├── admin_dashboard.html     # Admin dashboard with stats
│   │   ├── login.html
│   │   └── users/                   # User management templates
│   │
│   ├── employees/                   # Employee templates
│   │   ├── employee_list.html
│   │   ├── employee_detail.html
│   │   └── employee_form.html
│   │
│   ├── sites/                       # Site templates
│   │   └── site_list.html
│   │
│   ├── projects/                    # Project templates
│   │   └── project_list.html
│   │
│   ├── attendance/                  # Attendance templates
│   │   ├── attendance_list.html     # Main attendance page
│   │   ├── manage_attendance.html
│   │   ├── quick_attendance.html
│   │   ├── bulk_attendance.html
│   │   ├── attendance_form.html
│   │   ├── attendance_confirm_delete.html
│   │   └── includes/                # Modal partials
│   │       ├── attendance_modal.html
│   │       └── attendance_delete_modal.html
│   │
│   ├── timesheets/                  # (empty)
│   ├── payroll/                     # (empty)
│   └── documents/                   # (empty)
│
├── static/                          # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
│
├── media/                           # Uploaded files (gitignored)
│   └── documents/                   # Document uploads
│
├── requirements.txt                 # Python dependencies
├── manage.py                        # Django management script
├── db.sqlite3                       # SQLite database (gitignored)
├── .gitignore                       # Git ignore rules
└── README.md                        # This file
```

---

## 💰 Payroll Calculations

### Overtime Pay Formula
```
Overtime Pay = (Basic Salary / 30 / 8) × 1.5 × Overtime Hours
```

**Breakdown**:
- `Basic Salary / 30` = Daily rate
- `Daily Rate / 8` = Hourly rate
- `Hourly Rate × 1.5` = Overtime hourly rate (1.5x normal rate)
- `Overtime Hourly Rate × Overtime Hours` = Total overtime pay

### Net Salary Formula
```
Net Salary = Basic Salary + Allowances + Overtime Pay - Deductions
```

---

## 🌐 GitHub Repository

**Repository**: https://github.com/ademabdrei/longwayems

**Branch**: `main`

**Clone**:
```bash
git clone https://github.com/ademabdrei/longwayems.git
```

---

## 📝 License

This project is proprietary software. All rights reserved.

---

## 🆘 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Contact your system administrator

---

**© 2024-2026 Employee Management System. All rights reserved.**
