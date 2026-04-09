# Employee Management System (EMS)

A comprehensive Django-based Employee Management System designed for construction and field-based companies operating in the UAE. This system manages employees, sites, projects, attendance, payroll, timesheets, and documents with role-based access control.

## ✨ Key Features

- **User Authentication & Authorization**: Session-based authentication with three roles (Admin, Manager, Employee)
- **Employee Management**: Complete CRUD operations for employee profiles
- **Site & Project Management**: Track sites and projects with employee assignments
- **Advanced Attendance Tracking**: 
  - Inline dropdown status selection with color-coded badges
  - Bulk update toolbar for multiple employees
  - Project-specific attendance tracking
  - Overtime and notes support
  - Smart partial updates (only modify fields you fill in)
  - Beautiful toast notifications with detailed update info
- **Timesheets**: Multi-project daily timesheet entries
- **Payroll Management**: Automated payroll generation with overtime calculations
- **Document Management**: File uploads and management per employee/project
- **Audit Trail**: Full audit logging using django-auditlog
- **Export Functionality**: Excel and PDF exports for reports and payslips
- **Responsive UI**: Bootstrap 5-based responsive design

## 📸 Attendance Module Features

### Smart Attendance Page
- **Statistics Cards**: Quick overview of Total, Present, Absent, Night, Double, Unmarked counts
- **Site-Based Filtering**: Sidebar navigation by site
- **Inline Status Dropdowns**: Change attendance directly from the table with color-coded options
- **Bulk Update Toolbar**: Select multiple employees and update status, overtime, or notes at once
- **Partial Updates**: Only fills in what you provide - existing values are preserved
- **Auto-Refresh**: Page refreshes after any update to show fresh data
- **Toast Notifications**: Centered, beautiful notifications with employee names and update details

### Attendance Status Options
- ✅ Present
- ❌ Absent
- 🌙 Night
- ☀️ Double
- ⚪ Half
- 📅 On Leave
- ➖ Unmarked

## 🛠 Tech Stack

- **Backend**: Django 4.2+ (Pure Django, NO Django REST Framework)
- **Frontend**: Django HTML Templates + Bootstrap 5 + Bootstrap Icons
- **Database**: SQLite (default for local development)
- **Authentication**: Django built-in session-based authentication
- **Admin**: Heavily customized Django Admin Panel
- **Audit Trail**: django-auditlog
- **File Storage**: Local media folder
- **Exports**: Excel (openpyxl) + PDF (reportlab)
- **AJAX**: Vanilla JavaScript for dynamic updates without page reloads

## 📋 Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git (for cloning the repository)

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ademabdrei/longwayems.git
cd longwayems
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

## 🔑 Default Login Credentials

After creating a superuser, you can log in with those credentials. To create additional users:

1. Log in as Admin
2. Navigate to **User Management** in the sidebar
3. Click **Add User** to create new Admin, Manager, or Employee accounts

## 📁 Folder Structure

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
│   ├── employees/           # Employee CRUD, profile, site assignments
│   ├── sites/               # Site management
│   ├── projects/            # Project CRUD, employee assignments
│   ├── attendance/          # Advanced attendance with bulk update
│   ├── timesheets/          # Multi-project daily timesheets
│   ├── payroll/             # Salary, overtime, payslips
│   └── documents/           # File uploads per employee/project
│
├── templates/               # Global templates folder
│   ├── base.html            # Base template with sidebar
│   ├── attendance/          # Attendance templates with modals
│   ├── employees/           # Employee templates
│   ├── sites/               # Site templates
│   ├── projects/            # Project templates
│   ├── timesheets/          # Timesheet templates
│   ├── payroll/             # Payroll templates
│   └── documents/           # Document templates
│
├── static/                  # CSS, JS, images
├── media/                   # Uploaded files (gitignored)
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## 📦 Module Descriptions

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
- View site assignments and project assignments
- Site assignment modal for quick assignment

### Sites Module
- Site list with emirate and status filters
- Create, edit, and delete sites
- Assign managers to sites
- View site details and employee counts

### Projects Module
- Project list with status and site filters
- Create, edit, and delete projects
- Assign employees to projects
- View project details and attendance stats

### Attendance Module ⭐ (Recently Enhanced)
- **Modern UI**: Clean statistics cards showing attendance breakdown
- **Inline Dropdowns**: Change status directly from table rows
- **Bulk Update Toolbar**: 
  - Select multiple employees via checkboxes
  - Update status, overtime hours, and notes in one click
  - Smart partial updates - only modify fields you fill in
  - Compact, sleek design
- **Project Tracking**: Assign employees to specific projects when marking attendance
- **Toast Notifications**: Centered, beautiful notifications with:
  - Employee names updated
  - Status applied
  - Count of employees affected
  - "Refreshing page..." indicator
- **Auto-Refresh**: Page automatically refreshes after updates to show fresh data
- **Site-Based Navigation**: Sidebar shows all sites with employee counts
- **AJAX Powered**: All updates happen without full page reloads until save

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

## 👥 Role-Based Access Control

### Admin
- Full access to ALL modules
- Can create/edit/delete users, employees, projects
- Can process payroll and mark attendance
- Can view all reports and export data
- Can access Django Admin panel (`/admin/`)

### Manager
- Can view/edit employees assigned to their sites/projects
- Can mark and edit attendance for their site's employees
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

## 🎯 How to Create the First Admin User

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

## 📊 How to Use the Attendance Module

### Quick Attendance (Individual)
1. Navigate to **Attendance** from the sidebar
2. Select a **Site** from the left sidebar (optional)
3. Use the **dropdown** in each employee row to change status
4. Page auto-refreshes to show the updated status

### Bulk Update Attendance
1. **Select employees** using the checkboxes in the table
   - Or use the **"Select All"** checkbox in the header
2. The **Bulk Update Toolbar** appears above the table
3. Fill in the fields you want to update:
   - **Status**: Choose attendance status (optional)
   - **OT hrs**: Enter overtime hours (optional)
   - **Notes**: Add notes for all selected employees (optional)
4. Click **"Apply"**
5. A beautiful toast notification shows the update details
6. Page refreshes with updated data

**Smart Partial Updates:**
- Leave status empty → existing status stays unchanged
- Leave overtime empty → existing overtime stays unchanged
- Leave notes empty → existing notes stay unchanged
- Only the fields you fill in will be updated!

## 📤 How to Run Exports

### Excel Exports
1. Navigate to the respective module (Employees, Attendance, Timesheets, Payroll)
2. Click the "Export" button (visible to Admin/Manager roles)
3. The file will download automatically with the format: `module_YYYY-MM-DD.xlsx`

### PDF Exports
1. **Payslip PDF**: Navigate to Payroll → View a payroll record → Click "Download Payslip PDF"
2. **Attendance PDF**: Navigate to Attendance → Summary → Select month/year → Click "Export PDF"

## 💰 Overtime Calculation Formula

The system calculates overtime pay using the following formula:

```
Overtime Pay = (Basic Salary / 30 / 8) × 1.5 × Overtime Hours
```

Where:
- `Basic Salary / 30` = Daily rate
- `Daily Rate / 8` = Hourly rate
- `Hourly Rate × 1.5` = Overtime hourly rate (1.5x normal rate)
- `Overtime Hourly Rate × Overtime Hours` = Total overtime pay

## 💵 Net Salary Calculation

```
Net Salary = Basic Salary + Allowances + Overtime Pay - Deductions
```

## 🔍 Audit Trail

All changes to the following models are logged:
- CustomUser
- Employee
- Site
- Project
- EmployeeProjectAssignment
- Attendance
- Timesheet
- Payroll
- Document

View the audit log at: **User Management → Activity Log** (Admin only)

## 🌐 GitHub Repository

**Repository**: https://github.com/ademabdrei/longwayems

## 📝 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For issues or questions, please contact your system administrator.

---

**© 2024-2026 Employee Management System. All rights reserved.**
