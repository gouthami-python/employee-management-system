from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employees.models import *
from datetime import datetime, timedelta, time
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating database...')

        # Create Departments
        departments = [
            {'name': 'IT', 'description': 'Information Technology'},
            {'name': 'HR', 'description': 'Human Resources'},
            {'name': 'Finance', 'description': 'Finance and Accounting'},
            {'name': 'Marketing', 'description': 'Marketing and Sales'},
            {'name': 'Operations', 'description': 'Operations Management'},
        ]
        
        dept_objs = []
        for dept in departments:
            d, _ = Department.objects.get_or_create(name=dept['name'], defaults={'description': dept['description']})
            dept_objs.append(d)
        self.stdout.write(f'[OK] Created {len(dept_objs)} departments')

        # Create Roles
        roles = [
            {'title': 'Manager', 'level': 5},
            {'title': 'Senior Developer', 'level': 4},
            {'title': 'Developer', 'level': 3},
            {'title': 'Junior Developer', 'level': 2},
            {'title': 'Intern', 'level': 1},
        ]
        
        role_objs = []
        for role in roles:
            r, _ = Role.objects.get_or_create(title=role['title'], defaults={'level': role['level']})
            role_objs.append(r)
        self.stdout.write(f'[OK] Created {len(role_objs)} roles')

        # Create Employees
        employees_data = [
            {'username': 'john.doe', 'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com', 'phone': '1234567890', 'dept': 0, 'role': 1, 'salary': 75000},
            {'username': 'jane.smith', 'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane@example.com', 'phone': '1234567891', 'dept': 1, 'role': 0, 'salary': 85000},
            {'username': 'bob.wilson', 'first_name': 'Bob', 'last_name': 'Wilson', 'email': 'bob@example.com', 'phone': '1234567892', 'dept': 2, 'role': 2, 'salary': 65000},
            {'username': 'alice.brown', 'first_name': 'Alice', 'last_name': 'Brown', 'email': 'alice@example.com', 'phone': '1234567893', 'dept': 3, 'role': 1, 'salary': 72000},
            {'username': 'charlie.davis', 'first_name': 'Charlie', 'last_name': 'Davis', 'email': 'charlie@example.com', 'phone': '1234567894', 'dept': 0, 'role': 3, 'salary': 55000},
            {'username': 'emma.jones', 'first_name': 'Emma', 'last_name': 'Jones', 'email': 'emma@example.com', 'phone': '1234567895', 'dept': 4, 'role': 2, 'salary': 68000},
            {'username': 'david.miller', 'first_name': 'David', 'last_name': 'Miller', 'email': 'david@example.com', 'phone': '1234567896', 'dept': 1, 'role': 2, 'salary': 66000},
            {'username': 'sarah.garcia', 'first_name': 'Sarah', 'last_name': 'Garcia', 'email': 'sarah@example.com', 'phone': '1234567897', 'dept': 2, 'role': 1, 'salary': 74000},
        ]
        
        emp_objs = []
        for emp_data in employees_data:
            if not User.objects.filter(username=emp_data['username']).exists():
                user = User.objects.create_user(
                    username=emp_data['username'],
                    email=emp_data['email'],
                    password='password123',
                    first_name=emp_data['first_name'],
                    last_name=emp_data['last_name']
                )
                employee = Employee.objects.create(
                    user=user,
                    employee_id=f'EMP{user.id:04d}',
                    department=dept_objs[emp_data['dept']],
                    role=role_objs[emp_data['role']],
                    phone=emp_data['phone'],
                    salary=emp_data['salary'],
                    date_joined=datetime.now().date() - timedelta(days=random.randint(30, 365))
                )
                emp_objs.append(employee)
        self.stdout.write(f'[OK] Created {len(emp_objs)} employees')

        # Create Tasks
        if emp_objs:
            task_titles = [
                'Update website homepage',
                'Fix login bug',
                'Prepare quarterly report',
                'Review employee performance',
                'Update database schema',
                'Create marketing campaign',
                'Conduct team meeting',
                'Deploy new features',
            ]
            
            for i, title in enumerate(task_titles):
                Task.objects.get_or_create(
                    title=title,
                    defaults={
                        'description': f'Description for {title}',
                        'assigned_to': random.choice(emp_objs),
                        'status': random.choice(['pending', 'in_progress', 'completed']),
                        'priority': random.choice(['low', 'medium', 'high']),
                    }
                )
            self.stdout.write(f'[OK] Created {len(task_titles)} tasks')

        # Create Announcements
        announcements = [
            {'title': 'Company Holiday - Diwali', 'content': 'Office will be closed on November 12th for Diwali celebration. Wishing everyone a happy and prosperous Diwali!'},
            {'title': 'New Attendance Policy', 'content': 'Updated attendance policy is now in effect. Please ensure to check-in before 9:30 AM to avoid late marking. Review the policy document on the portal.'},
            {'title': 'Team Building Event', 'content': 'Annual team building event scheduled for December 15th at Resort Valley. Registration is mandatory. Contact HR for details.'},
            {'title': 'Performance Review Cycle', 'content': 'Q4 performance reviews will begin from December 1st. Please complete your self-assessment forms by November 30th.'},
            {'title': 'New Employee Onboarding', 'content': 'Welcome our new team members joining this month! Orientation sessions will be held every Monday at 10 AM.'},
            {'title': 'IT Security Update', 'content': 'Mandatory password reset required for all employees. Please update your passwords by end of this week. Contact IT support for assistance.'},
            {'title': 'Health Insurance Enrollment', 'content': 'Open enrollment for health insurance is now active. Submit your forms to HR by November 25th. New plans available with better coverage.'},
            {'title': 'Office Renovation Notice', 'content': 'The 3rd floor will undergo renovation from December 5-10. Affected employees will be temporarily relocated to the 2nd floor.'},
            {'title': 'Training Program Launch', 'content': 'New skill development program launching next month. Topics include Python, React, and Project Management. Register through the learning portal.'},
            {'title': 'Year-End Bonus Announcement', 'content': 'Performance-based year-end bonuses will be processed with December salary. Congratulations to all eligible employees!'},
        ]
        
        admin_user = User.objects.filter(is_staff=True).first()
        if admin_user:
            for ann in announcements:
                Announcement.objects.get_or_create(
                    title=ann['title'],
                    defaults={'content': ann['content'], 'created_by': admin_user}
                )
            self.stdout.write(f'[OK] Created {len(announcements)} announcements')

        # Create Leave Requests
        if emp_objs:
            for i in range(5):
                Leave.objects.get_or_create(
                    employee=random.choice(emp_objs),
                    start_date=datetime.now().date() + timedelta(days=random.randint(1, 30)),
                    defaults={
                        'leave_type': random.choice(['sick', 'casual', 'vacation']),
                        'end_date': datetime.now().date() + timedelta(days=random.randint(31, 35)),
                        'reason': 'Personal reasons',
                        'status': random.choice(['pending', 'approved', 'rejected']),
                    }
                )
            self.stdout.write('[OK] Created 5 leave requests')

        # Create Complaints
        if emp_objs:
            complaints = [
                {'subject': 'AC not working', 'description': 'The AC in office is not working properly.'},
                {'subject': 'Parking issue', 'description': 'Need more parking space.'},
                {'subject': 'Internet slow', 'description': 'Internet connection is very slow.'},
            ]
            
            for comp in complaints:
                Complaint.objects.get_or_create(
                    subject=comp['subject'],
                    defaults={
                        'employee': random.choice(emp_objs),
                        'description': comp['description'],
                        'status': random.choice(['open', 'in_progress', 'resolved']),
                    }
                )
            self.stdout.write(f'[OK] Created {len(complaints)} complaints')

        # Create Attendance Records
        if emp_objs:
            today = datetime.now().date()
            all_employees = Employee.objects.all()
            
            # Create today's attendance for all employees
            for emp in all_employees:
                if not Attendance.objects.filter(employee=emp, date=today).exists():
                    check_in = time(9, random.randint(0, 45))
                    check_out = time(17, random.randint(0, 59)) if random.choice([True, False]) else None
                    Attendance.objects.create(
                        employee=emp,
                        date=today,
                        check_in=check_in,
                        check_out=check_out,
                        status='present',
                        is_late=check_in > time(9, 30)
                    )
            
            # Create past attendance records
            for days_ago in range(1, 10):
                date = today - timedelta(days=days_ago)
                for emp in all_employees[:5]:  # Only for first 5 employees
                    if not Attendance.objects.filter(employee=emp, date=date).exists():
                        check_in = time(9, random.randint(0, 45))
                        check_out = time(17, random.randint(0, 59))
                        Attendance.objects.create(
                            employee=emp,
                            date=date,
                            check_in=check_in,
                            check_out=check_out,
                            status='present',
                            is_late=check_in > time(9, 30)
                        )
            self.stdout.write('[OK] Created attendance records including today\'s data')

        # Create Job Vacancies
        if admin_user:
            vacancies = [
                {'title': 'Senior Python Developer', 'dept': 0, 'salary': '$80,000 - $100,000'},
                {'title': 'HR Manager', 'dept': 1, 'salary': '$70,000 - $90,000'},
                {'title': 'Marketing Specialist', 'dept': 3, 'salary': '$60,000 - $75,000'},
            ]
            
            for vac in vacancies:
                JobVacancy.objects.get_or_create(
                    title=vac['title'],
                    defaults={
                        'department': dept_objs[vac['dept']],
                        'description': f'Looking for {vac["title"]}',
                        'requirements': 'Bachelor degree and 3+ years experience',
                        'salary_range': vac['salary'],
                        'location': 'New York',
                        'status': 'open',
                        'closing_date': datetime.now().date() + timedelta(days=30),
                        'created_by': admin_user,
                    }
                )
            self.stdout.write(f'[OK] Created {len(vacancies)} job vacancies')

        # Create Salary Structures
        if emp_objs:
            for emp in emp_objs[:3]:
                if not SalaryStructure.objects.filter(employee=emp).exists():
                    basic = Decimal(emp.salary) * Decimal('0.6')
                    SalaryStructure.objects.create(
                        employee=emp,
                        basic_pay=basic,
                        hra=basic * Decimal('0.3'),
                        transport_allowance=Decimal('2000'),
                        medical_allowance=Decimal('1500'),
                        effective_from=datetime.now().date() - timedelta(days=30)
                    )
            self.stdout.write('[OK] Created salary structures')

        # Create Salary History
        if emp_objs and admin_user:
            all_employees = Employee.objects.all()
            reasons = ['Annual increment', 'Performance bonus', 'Promotion', 'Market adjustment', 'Cost of living adjustment', 'Role change']
            
            for emp in all_employees:
                current_salary = emp.salary
                num_changes = random.randint(2, 4)
                
                for i in range(num_changes):
                    months_ago = (i + 1) * random.randint(3, 6)
                    old_salary = current_salary - random.randint(3000, 8000)
                    
                    history = SalaryHistory.objects.create(
                        employee=emp,
                        old_salary=old_salary,
                        new_salary=current_salary,
                        change_type='increment',
                        reason=random.choice(reasons),
                        changed_by=admin_user
                    )
                    history.changed_at = datetime.now() - timedelta(days=months_ago * 30)
                    history.save()
                    
                    current_salary = old_salary
            
            self.stdout.write(f'[OK] Created salary history for {all_employees.count()} employees')

        # Create Bonuses
        if emp_objs and admin_user:
            bonus_types = ['performance', 'festival', 'annual', 'other']
            bonus_reasons = [
                'Excellent performance in Q4',
                'Diwali festival bonus',
                'Annual performance bonus',
                'Project completion bonus',
                'Client appreciation bonus',
            ]
            
            for emp in emp_objs[:5]:
                for i in range(random.randint(1, 3)):
                    Bonus.objects.get_or_create(
                        employee=emp,
                        amount=random.choice([5000, 10000, 15000, 20000]),
                        defaults={
                            'bonus_type': random.choice(bonus_types),
                            'reason': random.choice(bonus_reasons),
                            'given_by': admin_user,
                        }
                    )
            self.stdout.write('[OK] Created bonus records')

        # Create Attendance Corrections
        if emp_objs:
            attendances = Attendance.objects.filter(employee__in=emp_objs[:3])[:3]
            for att in attendances:
                if not AttendanceCorrection.objects.filter(attendance=att).exists():
                    AttendanceCorrection.objects.create(
                        employee=att.employee,
                        attendance=att,
                        reason='Checked out by mistake, was still working',
                        status=random.choice(['pending', 'approved', 'rejected'])
                    )
            self.stdout.write('[OK] Created attendance correction requests')

        # Create Password Reset Requests
        if emp_objs:
            for emp in emp_objs[:2]:
                if not PasswordResetRequest.objects.filter(employee=emp).exists():
                    PasswordResetRequest.objects.create(
                        employee=emp,
                        reason='Forgot password',
                        new_password='newpass123',
                        status='pending'
                    )
            self.stdout.write('[OK] Created password reset requests')

        # Create Reviews
        if emp_objs and len(emp_objs) > 1:
            for emp in emp_objs[:3]:
                if not Review.objects.filter(employee=emp).exists():
                    Review.objects.create(
                        employee=emp,
                        reviewer=emp_objs[0],
                        rating=random.randint(3, 5),
                        feedback='Good performance overall',
                        review_period_start=datetime.now().date() - timedelta(days=90),
                        review_period_end=datetime.now().date()
                    )
            self.stdout.write('[OK] Created performance reviews')

        # Create Job Applications
        vacancies = JobVacancy.objects.all()
        if vacancies:
            applicants = [
                {'name': 'Michael Johnson', 'email': 'michael@example.com', 'phone': '9876543210', 'resume': 'resumes/Michael_Johnson_Resume.pdf'},
                {'name': 'Lisa Anderson', 'email': 'lisa@example.com', 'phone': '9876543211', 'resume': 'resumes/Lisa_Anderson_Resume.pdf'},
                {'name': 'Robert Taylor', 'email': 'robert@example.com', 'phone': '9876543212', 'resume': 'resumes/Robert_Taylor_Resume.pdf'},
                {'name': 'Emily Davis', 'email': 'emily@example.com', 'phone': '9876543213', 'resume': 'resumes/Emily_Davis_Resume.pdf'},
                {'name': 'James Wilson', 'email': 'james@example.com', 'phone': '9876543214', 'resume': 'resumes/James_Wilson_Resume.pdf'},
                {'name': 'Sophia Martinez', 'email': 'sophia@example.com', 'phone': '9876543215', 'resume': 'resumes/Sophia_Martinez_Resume.pdf'},
                {'name': 'Daniel Brown', 'email': 'daniel@example.com', 'phone': '9876543216', 'resume': 'resumes/Daniel_Brown_Resume.pdf'},
                {'name': 'Olivia Garcia', 'email': 'olivia@example.com', 'phone': '9876543217', 'resume': 'resumes/Olivia_Garcia_Resume.pdf'},
                {'name': 'William Lee', 'email': 'william@example.com', 'phone': '9876543218', 'resume': 'resumes/William_Lee_Resume.pdf'},
                {'name': 'Ava Thompson', 'email': 'ava@example.com', 'phone': '9876543219', 'resume': 'resumes/Ava_Thompson_Resume.pdf'},
            ]
            
            for applicant in applicants:
                JobApplication.objects.get_or_create(
                    email=applicant['email'],
                    defaults={
                        'vacancy': random.choice(vacancies),
                        'applicant_name': applicant['name'],
                        'phone': applicant['phone'],
                        'resume': applicant['resume'],
                        'cover_letter': 'I am interested in this position and believe my skills align well with the requirements.',
                        'status': random.choice(['submitted', 'under_review', 'shortlisted', 'rejected']),
                    }
                )
            self.stdout.write('[OK] Created 10 job applications with resumes')

        self.stdout.write(self.style.SUCCESS('\n[SUCCESS] Database populated successfully!'))
        self.stdout.write('\nLogin credentials:')
        self.stdout.write('Admin: username=admin, password=admin123')
        self.stdout.write('Employees: username=john.doe (or any employee), password=password123')
