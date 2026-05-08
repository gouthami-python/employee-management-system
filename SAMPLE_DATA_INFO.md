# Sample Data Information

## Overview
The database has been populated with comprehensive sample data for all features in the Employee Management System.

## What's Included

### 1. **Departments** (5)
- IT (Information Technology)
- HR (Human Resources)
- Finance (Finance and Accounting)
- Marketing (Marketing and Sales)
- Operations (Operations Management)

### 2. **Roles** (5)
- Manager (Level 5)
- Senior Developer (Level 4)
- Developer (Level 3)
- Junior Developer (Level 2)
- Intern (Level 1)

### 3. **Employees** (8)
All employees have password: `password123`

| Username | Name | Department | Role | Salary |
|----------|------|------------|------|--------|
| john.doe | John Doe | IT | Senior Developer | $75,000 |
| jane.smith | Jane Smith | HR | Manager | $85,000 |
| bob.wilson | Bob Wilson | Finance | Developer | $65,000 |
| alice.brown | Alice Brown | Marketing | Senior Developer | $72,000 |
| charlie.davis | Charlie Davis | IT | Junior Developer | $55,000 |
| emma.jones | Emma Jones | Operations | Developer | $68,000 |
| david.miller | David Miller | HR | Developer | $66,000 |
| sarah.garcia | Sarah Garcia | Finance | Senior Developer | $74,000 |

### 4. **Tasks** (8)
- Update website homepage
- Fix login bug
- Prepare quarterly report
- Review employee performance
- Update database schema
- Create marketing campaign
- Conduct team meeting
- Deploy new features

Status: Mix of Pending, In Progress, and Completed
Priority: Mix of Low, Medium, and High

### 5. **Announcements** (3)
- Company Holiday - Office closure notification
- New Policy Update - Attendance policy update
- Team Building Event - Upcoming team activities

### 6. **Leave Requests** (5)
- Various employees with different leave types (Sick, Casual, Vacation)
- Status: Mix of Pending, Approved, and Rejected
- Date ranges: Next 1-35 days

### 7. **Complaints** (3)
- AC not working
- Parking issue
- Internet slow

Status: Mix of Open, In Progress, and Resolved

### 8. **Attendance Records** (50)
- Last 10 days of attendance for 5 employees
- Includes check-in and check-out times
- Late arrival tracking (after 9:30 AM)

### 9. **Attendance Correction Requests** (3)
- Sample correction requests from employees
- Reason: "Checked out by mistake, was still working"
- Status: Mix of Pending, Approved, and Rejected

### 10. **Password Reset Requests** (2)
- 2 employees with pending password reset requests
- Reason: "Forgot password"
- New password: "newpass123"

### 11. **Salary History** (8-12 records)
- 2-3 salary changes per employee (first 4 employees)
- Shows progression from lower to current salary
- Change types: Increment
- Reasons include:
  - Annual increment
  - Performance bonus
  - Promotion
  - Market adjustment

### 12. **Bonuses** (5-15 records)
- 1-3 bonuses per employee (first 5 employees)
- Amounts: $5,000, $10,000, $15,000, $20,000
- Types: Performance, Festival, Annual, Other
- Reasons include:
  - Excellent performance in Q4
  - Diwali festival bonus
  - Annual performance bonus
  - Project completion bonus
  - Client appreciation bonus

### 13. **Performance Reviews** (3)
- Reviews for first 3 employees
- Ratings: 3-5 stars
- Feedback: "Good performance overall"
- Review period: Last 90 days

### 14. **Job Vacancies** (3)
- Senior Python Developer (IT) - $80,000 - $100,000
- HR Manager (HR) - $70,000 - $90,000
- Marketing Specialist (Marketing) - $60,000 - $75,000

Status: Open
Location: New York
Closing: 30 days from now

### 15. **Job Applications** (3)
Applicants:
- Michael Johnson (michael@example.com)
- Lisa Anderson (lisa@example.com)
- Robert Taylor (robert@example.com)

Status: Mix of Submitted, Under Review, and Shortlisted

### 16. **Salary Structures** (3)
- Created for first 3 employees
- Breakdown includes:
  - Basic Pay (60% of total)
  - HRA (30% of basic)
  - Transport Allowance ($2,000)
  - Medical Allowance ($1,500)

## Login Credentials

### Admin Account
- **Username:** admin
- **Password:** admin123
- **Access:** Full admin panel with all features

### Employee Accounts
- **Username:** john.doe (or any employee from the list above)
- **Password:** password123
- **Access:** Employee portal with personal features

## How to Use

1. **Login as Admin:**
   - Go to http://127.0.0.1:8000/admin-login/
   - Use admin/admin123
   - Access all admin features

2. **Login as Employee:**
   - Go to http://127.0.0.1:8000/employee-login/
   - Use john.doe/password123 (or any other employee)
   - Access employee portal

3. **Test Features:**
   - View salary history for employees
   - Check bonus records
   - Review attendance corrections
   - Approve/reject leave requests
   - Respond to complaints
   - Manage tasks and announcements

## Re-populate Data

If you want to refresh the sample data:

```bash
python manage.py populate_data
```

Note: This will add new data without deleting existing records. To start fresh, delete the database file and run migrations again.

## Features Covered

✅ Employee Management
✅ Department Management
✅ Task Management
✅ Announcement System
✅ Leave Management
✅ Complaint System
✅ Attendance Tracking
✅ Attendance Corrections
✅ Password Reset Requests
✅ Salary Management
✅ Salary History Tracking
✅ Bonus Management
✅ Performance Reviews
✅ Job Vacancies
✅ Job Applications
✅ Salary Structures

All features now have sample data for testing and demonstration!
