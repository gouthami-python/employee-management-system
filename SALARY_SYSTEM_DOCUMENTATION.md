# Salary Management System Documentation

## Overview
A comprehensive salary management system integrated into the Employee Management System with role-based access for Admin and Employee users.

## Database Structure

### 1. SalaryStructure Model
- **employee**: ForeignKey to Employee (one-to-many)
- **basic_pay**: DecimalField - Base salary amount
- **hra**: DecimalField - House Rent Allowance
- **transport_allowance**: DecimalField - Transportation allowance
- **medical_allowance**: DecimalField - Medical benefits
- **other_allowances**: DecimalField - Additional allowances
- **pf_rate**: DecimalField - Provident Fund percentage (default 12%)
- **esi_rate**: DecimalField - ESI percentage (default 0.75%)
- **pt_amount**: DecimalField - Professional Tax fixed amount
- **is_active**: BooleanField - Active status
- **effective_from**: DateField - Effective date
- **gross_salary**: Property - Auto-calculated total earnings

### 2. SalaryRecord Model
- **employee**: ForeignKey to Employee
- **salary_structure**: ForeignKey to SalaryStructure
- **month/year**: Integer fields for salary period
- **Earnings**: basic_pay, hra, allowances, bonus, overtime
- **Deductions**: pf_employee, pf_employer, esi_employee, esi_employer, professional_tax, income_tax, other_deductions
- **Calculated Fields**: gross_salary, total_deductions, net_salary
- **status**: CharField (pending, paid, cancelled)
- **generated_at/paid_at**: DateTime fields
- **generated_by**: ForeignKey to User

## Features Implemented

### Admin Features

#### 1. Salary Structure Management
- **Add Salary Structure**: Create salary components for employees
- **View Structures**: List all active salary structures
- **Auto-deactivation**: Previous structures become inactive when new ones are added
- **Real-time Calculations**: Live calculation of gross salary and deductions

#### 2. Salary Generation
- **Monthly Salary Creation**: Generate salary for specific month/year
- **Auto-calculations**: 
  - PF: Employee (12% of basic) + Employer (same as employee)
  - ESI: Employee (0.75% of gross) + Employer (3.25% of gross)
  - Professional Tax: Fixed amount
- **Additional Components**: Bonus, overtime, income tax, other deductions
- **Duplicate Prevention**: Cannot generate salary twice for same period

#### 3. Salary Management
- **Salary List**: View all salary records with filters
- **Advanced Filtering**: By employee, month, year, status
- **Mark as Paid**: Update salary status to paid
- **PDF Generation**: Generate salary slips

#### 4. Reporting & Analytics
- **Comprehensive View**: All salary components breakdown
- **Status Tracking**: Pending, paid, cancelled statuses
- **Audit Trail**: Track who generated salary and when

### Employee Features

#### 1. Salary History
- **Personal Records**: View own salary history
- **Monthly Breakdown**: Detailed earnings and deductions
- **Status Visibility**: See payment status

#### 2. Salary Details
- **Comprehensive View**: Complete salary breakdown
- **Earnings Section**: All income components
- **Deductions Section**: All deduction components
- **Employer Contributions**: PF and ESI employer portions

#### 3. Salary Slip Download
- **PDF Generation**: Professional salary slip format
- **Company Branding**: TechCorp Solutions header
- **Detailed Breakdown**: All components listed
- **Secure Access**: Employees can only access own slips

## Salary Calculation Logic

### Earnings Calculation
```
Gross Salary = Basic Pay + HRA + Transport Allowance + Medical Allowance + Other Allowances + Bonus + Overtime
```

### Deductions Calculation
```
PF Employee = Basic Pay × PF Rate / 100
PF Employer = PF Employee (same amount)
ESI Employee = Gross Salary × ESI Rate / 100
ESI Employer = Gross Salary × 3.25 / 100
Total Deductions = PF Employee + ESI Employee + Professional Tax + Income Tax + Other Deductions
```

### Net Salary Calculation
```
Net Salary = Gross Salary - Total Deductions
```

## UI/UX Design Features

### Modern Interface
- **Bootstrap 5**: Responsive design framework
- **Color-coded Cards**: Green for earnings, red for deductions
- **Interactive Forms**: Real-time calculations
- **Professional Layout**: Clean, organized presentation

### User Experience
- **Intuitive Navigation**: Clear menu structure
- **Quick Actions**: One-click operations
- **Visual Feedback**: Status badges and alerts
- **Responsive Design**: Mobile-friendly interface

### Salary Slip Design
- **Professional Format**: Company letterhead style
- **Clear Sections**: Earnings, deductions, totals
- **Currency Formatting**: Indian Rupee symbol (₹)
- **Comprehensive Details**: All salary components

## Security Features

### Access Control
- **Role-based Access**: Admin vs Employee permissions
- **Data Isolation**: Employees see only own records
- **Secure PDF Access**: Authentication required

### Data Validation
- **Duplicate Prevention**: Unique constraints on salary records
- **Input Validation**: Form validation for all fields
- **Calculation Accuracy**: Decimal precision for financial data

## API Endpoints

### Admin Endpoints
- `GET /admin-panel/salary/` - Salary list with filters
- `GET /admin-panel/salary/structures/` - View salary structures
- `POST /admin-panel/salary/structures/add/` - Add salary structure
- `POST /admin-panel/salary/generate/` - Generate monthly salary
- `POST /admin-panel/salary/<id>/mark-paid/` - Mark salary as paid

### Employee Endpoints
- `GET /salary/` - Personal salary history
- `GET /salary/<id>/` - Salary detail view
- `GET /salary/<id>/pdf/` - Download salary slip PDF

### Shared Endpoints
- `GET /salary/<id>/pdf/` - PDF generation (role-based access)

## Installation & Setup

### Database Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### Dependencies
```bash
pip install reportlab  # For PDF generation
```

### URL Configuration
All salary URLs are automatically included in the main URL configuration.

### Navigation Integration
Salary management links are added to both admin and employee sidebars.

## Usage Workflow

### Admin Workflow
1. **Setup Salary Structure**
   - Navigate to Salary Management → Salary Structures
   - Add salary structure for each employee
   - Set basic pay, allowances, and deduction rates

2. **Generate Monthly Salary**
   - Go to Salary Management → Generate Salary
   - Select employee, month, and year
   - Add any bonus, overtime, or additional deductions
   - System auto-calculates all components

3. **Manage Salary Records**
   - View all salary records with filtering
   - Mark salaries as paid when processed
   - Generate PDF slips for employees

### Employee Workflow
1. **View Salary History**
   - Navigate to My Salary
   - See all salary records chronologically

2. **Check Salary Details**
   - Click on any salary record
   - View complete breakdown of earnings and deductions

3. **Download Salary Slip**
   - Click PDF button to download official salary slip
   - Print or save for records

## Calculation Examples

### Example Salary Structure
- Basic Pay: ₹50,000
- HRA: ₹15,000
- Transport: ₹2,000
- Medical: ₹1,500
- Other: ₹1,500
- **Gross**: ₹70,000

### Calculated Deductions
- PF Employee: ₹6,000 (12% of ₹50,000)
- PF Employer: ₹6,000
- ESI Employee: ₹525 (0.75% of ₹70,000)
- ESI Employer: ₹2,275 (3.25% of ₹70,000)
- Professional Tax: ₹200
- **Total Deductions**: ₹6,725

### Net Salary
- **Net Salary**: ₹63,275 (₹70,000 - ₹6,725)

## Future Enhancements

### Potential Features
- **Bulk Salary Generation**: Generate for multiple employees
- **Salary Revision History**: Track salary changes over time
- **Tax Calculation**: Automated income tax calculation
- **Payroll Integration**: Connect with payroll systems
- **Email Notifications**: Auto-send salary slips via email
- **Advanced Reporting**: Salary analytics and reports
- **Mobile App**: Native mobile application
- **Bank Integration**: Direct salary transfer

### Compliance Features
- **Statutory Compliance**: PF, ESI, PT compliance reports
- **Tax Reports**: Form 16, TDS certificates
- **Audit Trail**: Complete salary processing history
- **Backup & Recovery**: Data protection measures

This salary management system provides a robust foundation for payroll processing with room for future enhancements based on organizational requirements.