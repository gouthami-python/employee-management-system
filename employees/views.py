# employees/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from .models import *
from .models import AttendanceCorrection
from .forms import (
    EmployeeForm, DepartmentForm, TaskForm, AnnouncementForm, LeaveForm, 
    ComplaintForm, ReviewForm, JobVacancyForm, JobApplicationForm
)


def is_admin(user):
    """Check if user is admin/staff"""
    return user.is_staff or user.is_superuser


# DASHBOARD VIEWS

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard"""
    from django.db.models import Avg, Sum
    total_employees = Employee.objects.count()
    total_departments = Department.objects.count()
    active_tasks = Task.objects.filter(status__in=['pending', 'in_progress']).count()
    pending_leaves = Leave.objects.filter(status='pending').count()
    open_complaints = Complaint.objects.filter(status='open').count()
    recent_employees = Employee.objects.select_related('user', 'department').order_by('-id')[:5]
    
    total_tasks = Task.objects.count()
    completed_tasks = round((Task.objects.filter(status='completed').count() / total_tasks * 100) if total_tasks > 0 else 0)
    total_attendance = Attendance.objects.count()
    present_count = Attendance.objects.filter(status='present').count()
    attendance_rate = round((present_count / total_attendance * 100) if total_attendance > 0 else 0)
    avg_rating = Review.objects.aggregate(Avg('rating'))['rating__avg'] or 0
    avg_rating = round(avg_rating, 1)
    total_payroll = Employee.objects.aggregate(Sum('salary'))['salary__sum'] or 0
    
    context = {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'active_tasks': active_tasks,
        'pending_leaves': pending_leaves,
        'open_complaints': open_complaints,
        'recent_employees': recent_employees,
        'completed_tasks': completed_tasks,
        'attendance_rate': attendance_rate,
        'avg_rating': avg_rating,
        'total_payroll': total_payroll,
    }
    return render(request, 'admin/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_profile(request):
    """Admin profile view"""
    return render(request, 'admin/profile.html', {'user': request.user})


@login_required
def employee_dashboard(request):
    """Employee dashboard"""
    try:
        from django.db.models import Avg
        employee = request.user.employee
        my_tasks = Task.objects.filter(assigned_to=employee).order_by('-created_at')[:5]
        pending_tasks = Task.objects.filter(assigned_to=employee, status__in=['pending', 'in_progress']).count()
        completed_tasks = Task.objects.filter(assigned_to=employee, status='completed').count()
        my_leaves = Leave.objects.filter(employee=employee).order_by('-applied_at')[:3]
        
        total_tasks = Task.objects.filter(assigned_to=employee).count()
        task_completion = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)
        total_attendance = Attendance.objects.filter(employee=employee).count()
        present_count = Attendance.objects.filter(employee=employee, status='present').count()
        attendance_rate = round((present_count / total_attendance * 100) if total_attendance > 0 else 0)
        avg_rating = Review.objects.filter(employee=employee).aggregate(Avg('rating'))['rating__avg'] or 0
        avg_rating = round(avg_rating, 1)
        
        context = {
            'employee': employee,
            'my_tasks': my_tasks,
            'pending_tasks': pending_tasks,
            'completed_tasks': completed_tasks,
            'my_leaves': my_leaves,
            'task_completion': task_completion,
            'attendance_rate': attendance_rate,
            'avg_rating': avg_rating,
        }
        return render(request, 'employee/dashboard.html', context)
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found!')
        return redirect('home')


# EMPLOYEE MANAGEMENT VIEWS

@login_required
@user_passes_test(is_admin)
def employee_list(request):
    """List all employees with search and filter"""
    employees = Employee.objects.select_related('department', 'role', 'user').all()
    
    # Search
    search = request.GET.get('search', '')
    if search:
        employees = employees.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__username__icontains=search) |
            Q(employee_id__icontains=search)
        )
    
    # Filter by department
    department = request.GET.get('department', '')
    if department:
        employees = employees.filter(department_id=department)
    
    # Filter by position
    position = request.GET.get('position', '')
    if position:
        employees = employees.filter(position__icontains=position)
    
    departments = Department.objects.all()
    return render(request, 'admin/employee_list.html', {
        'employees': employees,
        'departments': departments,
        'search': search,
        'selected_department': department,
        'selected_position': position
    })


@login_required
@user_passes_test(is_admin)
def employee_add(request):
    """Add new employee"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                password='changeme123'
            )
            employee = form.save(commit=False)
            employee.user = user
            employee.save()
            messages.success(request, f'Employee {employee.employee_id} added successfully!')
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'admin/employee_form.html', {'form': form, 'action': 'Add'})


@login_required
@user_passes_test(is_admin)
def employee_edit(request, pk):
    """Edit existing employee"""
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            employee.user.first_name = form.cleaned_data.get('first_name', employee.user.first_name)
            employee.user.last_name = form.cleaned_data.get('last_name', employee.user.last_name)
            employee.user.email = form.cleaned_data.get('email', employee.user.email)
            
            # Update password if provided
            password = form.cleaned_data.get('password')
            if password:
                employee.user.set_password(password)
            
            employee.user.save()
            messages.success(request, 'Employee updated successfully!')
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee, initial={
            'first_name': employee.user.first_name,
            'last_name': employee.user.last_name,
            'email': employee.user.email,
            'username': employee.user.username,
        })
    return render(request, 'admin/employee_form.html', {'form': form, 'employee': employee, 'action': 'Edit'})


@login_required
@user_passes_test(is_admin)
def employee_delete(request, pk):
    """Delete employee"""
    employee = get_object_or_404(Employee, pk=pk)
    employee_id = employee.employee_id
    employee.user.delete()
    messages.success(request, f'Employee {employee_id} deleted successfully!')
    return redirect('employee_list')


# DEPARTMENT MANAGEMENT

@login_required
@user_passes_test(is_admin)
def department_list(request):
    departments = Department.objects.annotate(employee_count=Count('employee')).all()
    return render(request, 'admin/department_list.html', {'departments': departments})


@login_required
@user_passes_test(is_admin)
def department_add(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department added successfully!')
            return redirect('department_list')
    else:
        form = DepartmentForm()
    return render(request, 'admin/department_form.html', {'form': form, 'action': 'Add'})


@login_required
@user_passes_test(is_admin)
def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully!')
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'admin/department_form.html', {'form': form, 'department': department, 'action': 'Edit'})


@login_required
@user_passes_test(is_admin)
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    dept_name = department.name
    department.delete()
    messages.success(request, f'Department "{dept_name}" deleted successfully!')
    return redirect('department_list')


# TASK MANAGEMENT

@login_required
@user_passes_test(is_admin)
def task_list(request):
    tasks = Task.objects.select_related('assigned_to', 'assigned_by', 'department').all().order_by('-created_at')
    return render(request, 'admin/task_list.html', {'tasks': tasks})


@login_required
@user_passes_test(is_admin)
def task_assign(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            try:
                task.assigned_by = request.user.employee
            except Employee.DoesNotExist:
                messages.error(request, 'Admin employee profile not found!')
                return redirect('task_list')
            task.save()
            messages.success(request, f'Task "{task.title}" assigned successfully!')
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'admin/task_form.html', {'form': form, 'action': 'Assign'})


@login_required
@user_passes_test(is_admin)
def task_update_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            if new_status == 'completed':
                task.completed_at = timezone.now()
            task.save()
            messages.success(request, f'Task status updated to {task.get_status_display()}')
    return redirect('task_list')


# ANNOUNCEMENTS

@login_required
@user_passes_test(is_admin)
def announcement_list(request):
    announcements = Announcement.objects.select_related('created_by', 'department').order_by('-created_at')
    return render(request, 'admin/announcements.html', {'announcements': announcements})


@login_required
@user_passes_test(is_admin)
def announcement_add(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            messages.success(request, 'Announcement created successfully!')
            return redirect('announcement_list')
    else:
        form = AnnouncementForm()
    return render(request, 'admin/announcement_form.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def announcement_delete(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    title = announcement.title
    announcement.delete()
    messages.success(request, f'Announcement "{title}" deleted successfully!')
    return redirect('announcement_list')


# LEAVE MANAGEMENT

@login_required
@user_passes_test(is_admin)
def leave_requests(request):
    status_filter = request.GET.get('status', 'pending')
    if status_filter == 'all':
        leaves = Leave.objects.select_related('employee').all().order_by('-applied_at')
    else:
        leaves = Leave.objects.select_related('employee').filter(status=status_filter).order_by('-applied_at')
    return render(request, 'admin/leave_requests.html', {'leaves': leaves, 'status_filter': status_filter})


@login_required
@user_passes_test(is_admin)
def leave_approve(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    leave.status = 'approved'
    leave.reviewed_by = request.user
    leave.reviewed_at = timezone.now()
    if request.method == 'POST':
        leave.admin_remarks = request.POST.get('remarks', '')
    leave.save()
    messages.success(request, f'Leave request for {leave.employee} approved!')
    return redirect('leave_requests')


@login_required
@user_passes_test(is_admin)
def leave_reject(request, pk):
    leave = get_object_or_404(Leave, pk=pk)
    leave.status = 'rejected'
    leave.reviewed_by = request.user
    leave.reviewed_at = timezone.now()
    if request.method == 'POST':
        leave.admin_remarks = request.POST.get('remarks', '')
    leave.save()
    messages.success(request, f'Leave request for {leave.employee} rejected!')
    return redirect('leave_requests')


# COMPLAINTS

@login_required
@user_passes_test(is_admin)
def complaint_list(request):
    complaints = Complaint.objects.select_related('employee').order_by('-created_at')
    return render(request, 'admin/complaints.html', {'complaints': complaints})


@login_required
@user_passes_test(is_admin)
def complaint_respond(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if request.method == 'POST':
        response = request.POST.get('response')
        new_status = request.POST.get('status')
        complaint.admin_response = response
        complaint.status = new_status
        if new_status in ['resolved', 'closed']:
            complaint.resolved_at = timezone.now()
        complaint.save()
        messages.success(request, 'Response submitted successfully!')
        return redirect('complaint_list')
    return render(request, 'admin/complaint_respond.html', {'complaint': complaint})


# REVIEWS

@login_required
@user_passes_test(is_admin)
def review_list(request):
    reviews = Review.objects.select_related('employee', 'reviewer').order_by('-created_at')
    return render(request, 'admin/reviews.html', {'reviews': reviews})


@login_required
@user_passes_test(is_admin)
def review_add(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            try:
                review.reviewer = request.user.employee
            except Employee.DoesNotExist:
                messages.error(request, 'Admin employee profile not found!')
                return redirect('review_list')
            review.save()
            messages.success(request, f'Review for {review.employee} submitted successfully!')
            return redirect('review_list')
    else:
        form = ReviewForm()
    return render(request, 'admin/review_form.html', {'form': form})


# EMPLOYEE VIEWS

@login_required
def employee_tasks(request):
    try:
        employee = request.user.employee
        tasks = Task.objects.filter(assigned_to=employee).order_by('-created_at')
        status_filter = request.GET.get('status', 'all')
        if status_filter != 'all':
            tasks = tasks.filter(status=status_filter)
        return render(request, 'employee/tasks.html', {'tasks': tasks, 'status_filter': status_filter})
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found!')
        return redirect('home')


@login_required
def employee_task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, assigned_to=request.user.employee)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            if new_status == 'completed':
                task.completed_at = timezone.now()
            task.save()
            messages.success(request, f'Task status updated!')
    return redirect('employee_tasks')


@login_required
def employee_leave_apply(request):
    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.employee = request.user.employee
            leave.save()
            messages.success(request, 'Leave application submitted successfully!')
            return redirect('employee_leave_status')
    else:
        form = LeaveForm()
    return render(request, 'employee/leave_form.html', {'form': form})


@login_required
def employee_leave_status(request):
    leaves = Leave.objects.filter(employee=request.user.employee).order_by('-applied_at')
    return render(request, 'employee/leave_status.html', {'leaves': leaves})


@login_required
def employee_complaint_submit(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.employee = request.user.employee
            complaint.save()
            messages.success(request, 'Complaint submitted successfully!')
            return redirect('employee_complaint_track')
    else:
        form = ComplaintForm()
    return render(request, 'employee/complaint_form.html', {'form': form})


@login_required
def employee_complaint_track(request):
    complaints = Complaint.objects.filter(employee=request.user.employee).order_by('-created_at')
    return render(request, 'employee/complaint_track.html', {'complaints': complaints})


@login_required
def employee_profile(request):
    if request.user.is_staff:
        return render(request, 'admin/profile.html', {'user': request.user})
    try:
        employee = request.user.employee
        return render(request, 'employee/profile.html', {'employee': employee})
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found!')
        return redirect('employee_dashboard')


@login_required
def employee_feedback_submit(request):
    if request.method == 'POST':
        messages.success(request, 'Feedback submitted successfully!')
        return redirect('employee_tasks')
    return render(request, 'employee/feedback_form.html', {})


@login_required
def toggle_theme(request):
    if hasattr(request.user, 'employee'):
        employee = request.user.employee
        employee.theme_preference = 'dark' if employee.theme_preference == 'light' else 'light'
        employee.save()
    return redirect(request.META.get('HTTP_REFERER', 'employee_dashboard'))


# HOME & JOBS

def home(request):
    vacancies = JobVacancy.objects.filter(status='open').order_by('-posted_date')[:5]
    return render(request, 'home.html', {'vacancies': vacancies})


def job_apply(request, pk):
    vacancy = get_object_or_404(JobVacancy, pk=pk, status='open')
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.vacancy = vacancy
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('home')
    else:
        form = JobApplicationForm()
    return render(request, 'job_apply.html', {'form': form, 'vacancy': vacancy})


def job_list(request):
    vacancies = JobVacancy.objects.filter(status='open').order_by('-posted_date')
    return render(request, 'job_list.html', {'vacancies': vacancies})


def application_status(request):
    applications = None
    if request.method == 'POST':
        email = request.POST.get('email')
        applications = JobApplication.objects.filter(email=email).select_related('vacancy')
        if not applications:
            messages.error(request, 'No applications found for this email address.')
    return render(request, 'application_status.html', {'applications': applications})


@login_required
@user_passes_test(is_admin)
def vacancy_list(request):
    vacancies = JobVacancy.objects.all().order_by('-posted_date')
    return render(request, 'admin/vacancy_list.html', {'vacancies': vacancies})


@login_required
@user_passes_test(is_admin)
def vacancy_add(request):
    if request.method == 'POST':
        form = JobVacancyForm(request.POST)
        if form.is_valid():
            vacancy = form.save(commit=False)
            vacancy.created_by = request.user
            vacancy.save()
            messages.success(request, 'Job vacancy posted successfully!')
            return redirect('vacancy_list')
    else:
        form = JobVacancyForm()
    return render(request, 'admin/vacancy_form.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def application_list(request):
    vacancy_id = request.GET.get('vacancy')
    applications = JobApplication.objects.select_related('vacancy').order_by('-applied_date')
    vacancy = None
    
    if vacancy_id:
        vacancy = get_object_or_404(JobVacancy, pk=vacancy_id)
        applications = applications.filter(vacancy=vacancy)
    
    return render(request, 'admin/application_list.html', {
        'applications': applications,
        'vacancy': vacancy
    })


@login_required
@user_passes_test(is_admin)
def application_update(request, pk):
    from datetime import datetime
    application = get_object_or_404(JobApplication, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        notes = request.POST.get('notes')
        interview_date = request.POST.get('interview_date')
        interview_location = request.POST.get('interview_location')
        
        application.status = status
        application.notes = notes
        application.interview_location = interview_location
        application.reviewed_by = request.user
        
        if interview_date:
            application.interview_date = datetime.fromisoformat(interview_date)
        
        application.save()
        messages.success(request, f'Application status updated!')
        return redirect('application_list')
    return render(request, 'admin/application_update.html', {'application': application})


# AUTHENTICATION

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Access denied. Admin privileges required.')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'auth/admin_login.html')


def employee_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_staff:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                return redirect('employee_dashboard')
            else:
                messages.error(request, 'Access denied. Please use Admin Login.')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'auth/employee_login.html')


def employee_register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone', '')
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'auth/employee_register.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'auth/employee_register.html')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'auth/employee_register.html')
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            employee = Employee.objects.create(
                user=user,
                phone=phone,
                employee_id=f'EMP{user.id:04d}',
                position='Employee',
                salary=0.00
            )
            messages.success(request, 'Registration successful! You can now login.')
            return redirect('employee_login')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
    return render(request, 'auth/employee_register.html')


def logout_view(request):
    is_admin_user = request.user.is_staff
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    if is_admin_user:
        return redirect('admin_login')
    else:
        return redirect('employee_login')


# ATTENDANCE

@login_required
def employee_attendance(request):
    from datetime import datetime, time as dt_time
    employee = request.user.employee
    today = datetime.now().date()
    attendance_today = Attendance.objects.filter(employee=employee, date=today).first()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'check_in' and not attendance_today:
            check_in_time = datetime.now().time()
            is_late = check_in_time > dt_time(9, 30)
            Attendance.objects.create(
                employee=employee,
                date=today,
                check_in=check_in_time,
                status='present',
                is_late=is_late
            )
            messages.success(request, f'Checked in at {check_in_time.strftime("%I:%M %p")}')
        elif action == 'check_out' and attendance_today and not attendance_today.check_out:
            attendance_today.check_out = datetime.now().time()
            attendance_today.save()
            messages.success(request, f'Checked out at {attendance_today.check_out.strftime("%I:%M %p")}')
        return redirect('employee_attendance')
    
    attendances = Attendance.objects.filter(employee=employee).order_by('-date')[:30]
    return render(request, 'employee/attendance.html', {
        'attendance_today': attendance_today,
        'attendances': attendances
    })


@login_required
@user_passes_test(is_admin)
def admin_attendance_list(request):
    from datetime import datetime
    today = datetime.now().date()
    attendances = Attendance.objects.filter(date=today).select_related('employee')
    return render(request, 'admin/attendance_list.html', {'attendances': attendances, 'date': today})


@login_required
@user_passes_test(is_admin)
def admin_attendance_report(request):
    from datetime import datetime
    employees = Employee.objects.all()
    month = int(request.GET.get('month', datetime.now().month))
    year = int(request.GET.get('year', datetime.now().year))
    
    return render(request, 'admin/attendance_report.html', {
        'employees': employees,
        'month': month,
        'year': year
    })


@login_required
def employee_attendance_correction(request, pk):
    from datetime import datetime
    from .forms import AttendanceCorrectionForm
    from .models import AttendanceCorrection
    
    attendance = get_object_or_404(Attendance, pk=pk, employee=request.user.employee)
    
    if request.method == 'POST':
        form = AttendanceCorrectionForm(request.POST)
        if form.is_valid():
            correction = form.save(commit=False)
            correction.employee = request.user.employee
            correction.attendance = attendance
            correction.save()
            messages.success(request, 'Correction request submitted successfully!')
            return redirect('employee_attendance')
    else:
        form = AttendanceCorrectionForm()
    
    return render(request, 'employee/attendance_correction.html', {
        'form': form,
        'attendance': attendance
    })


@login_required
def employee_correction_status(request):
    from .models import AttendanceCorrection
    corrections = AttendanceCorrection.objects.filter(employee=request.user.employee).order_by('-requested_at')
    return render(request, 'employee/correction_status.html', {'corrections': corrections})


@login_required
@user_passes_test(is_admin)
def admin_correction_list(request):
    from .models import AttendanceCorrection
    corrections = AttendanceCorrection.objects.filter(status='pending').select_related('employee', 'attendance').order_by('-requested_at')
    return render(request, 'admin/correction_list.html', {'corrections': corrections})


@login_required
@user_passes_test(is_admin)
def admin_correction_review(request, pk):
    from datetime import datetime
    from .models import AttendanceCorrection
    
    correction = get_object_or_404(AttendanceCorrection, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        remarks = request.POST.get('remarks', '')
        
        if action == 'approve':
            correction.status = 'approved'
            correction.attendance.check_out = None
            correction.attendance.save()
            messages.success(request, 'Correction approved and checkout removed!')
        elif action == 'reject':
            correction.status = 'rejected'
            messages.success(request, 'Correction request rejected!')
        
        correction.admin_remarks = remarks
        correction.reviewed_by = request.user
        correction.reviewed_at = datetime.now()
        correction.save()
        
        return redirect('admin_correction_list')
    
    return render(request, 'admin/correction_review.html', {'correction': correction})


# PASSWORD RESET

def employee_forgot_password(request):
    if request.method == 'POST':
        from .forms import PasswordResetRequestForm
        from .models import PasswordResetRequest
        
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username, is_staff=False)
            employee = user.employee
            
            form = PasswordResetRequestForm(request.POST)
            if form.is_valid():
                reset_request = form.save(commit=False)
                reset_request.employee = employee
                reset_request.save()
                messages.success(request, 'Password reset request submitted! Admin will review it.')
                return redirect('employee_login')
        except User.DoesNotExist:
            messages.error(request, 'Username not found')
        except Employee.DoesNotExist:
            messages.error(request, 'Employee profile not found')
    else:
        from .forms import PasswordResetRequestForm
        form = PasswordResetRequestForm()
    
    return render(request, 'auth/forgot_password.html', {'form': form})


@login_required
def employee_password_reset_status(request):
    from .models import PasswordResetRequest
    requests = PasswordResetRequest.objects.filter(employee=request.user.employee).order_by('-requested_at')
    return render(request, 'employee/password_reset_status.html', {'requests': requests})


@login_required
@user_passes_test(is_admin)
def admin_password_reset_list(request):
    from .models import PasswordResetRequest
    requests = PasswordResetRequest.objects.filter(status='pending').select_related('employee').order_by('-requested_at')
    return render(request, 'admin/password_reset_list.html', {'requests': requests})


@login_required
@user_passes_test(is_admin)
def admin_password_reset_review(request, pk):
    from datetime import datetime
    from .models import PasswordResetRequest
    
    reset_request = get_object_or_404(PasswordResetRequest, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        remarks = request.POST.get('remarks', '')
        
        if action == 'approve':
            reset_request.status = 'approved'
            reset_request.employee.user.set_password(reset_request.new_password)
            reset_request.employee.user.save()
            messages.success(request, 'Password reset approved and updated!')
        elif action == 'reject':
            reset_request.status = 'rejected'
            messages.success(request, 'Password reset request rejected!')
        
        reset_request.admin_remarks = remarks
        reset_request.reviewed_by = request.user
        reset_request.reviewed_at = datetime.now()
        reset_request.save()
        
        return redirect('admin_password_reset_list')
    
    return render(request, 'admin/password_reset_review.html', {'reset_request': reset_request})


# SALARY MANAGEMENT

@login_required
@user_passes_test(is_admin)
def admin_salary_management(request):
    from .models import Employee, SalaryPayment, Bonus
    from .payroll_service import PayrollService
    from datetime import datetime
    
    # Handle salary payment
    if request.method == 'POST' and 'pay_salary' in request.POST:
        month = int(request.POST.get('month'))
        year = int(request.POST.get('year'))
        employee_ids = request.POST.getlist('employees')
        
        if not employee_ids:
            messages.error(request, 'Please select at least one employee')
            return redirect('admin_salary_management')
        
        # Check if should auto-approve
        auto_approve = request.POST.get('auto_approve') == 'true'
        
        # Process bulk payment with service
        results = PayrollService.process_bulk_payment(
            employee_ids=employee_ids,
            month=month,
            year=year,
            user=request.user,
            request=request,
            auto_approve=auto_approve,
            approval_threshold=10000
        )
        
        # Build success message
        batch = results['batch']
        msg_parts = []
        
        if batch.status == 'pending_approval':
            messages.info(request, f"Batch {batch.batch_id} created and pending approval. Total: ${batch.total_amount}")
        else:
            if results['successful']:
                msg_parts.append(f"✓ Paid {len(results['successful'])} employees")
            if results['skipped']:
                msg_parts.append(f"⊘ Skipped {len(results['skipped'])} (already paid)")
            if results['failed']:
                msg_parts.append(f"✗ Failed {len(results['failed'])} payments")
            
            if results['successful']:
                messages.success(request, ' | '.join(msg_parts) + f" for {month}/{year}")
            else:
                messages.warning(request, ' | '.join(msg_parts))
        
        return redirect('admin_salary_management')
    
    # Handle batch approval
    if request.method == 'POST' and 'approve_batch' in request.POST:
        batch_id = request.POST.get('batch_id')
        remarks = request.POST.get('remarks', '')
        
        result = PayrollService.approve_batch(batch_id, request.user, remarks)
        
        if result['success']:
            messages.success(request, f"Batch {result['batch'].batch_id} approved successfully!")
        else:
            messages.error(request, f"Approval failed: {result['message']}")
        
        return redirect('admin_salary_management')
    
    # Handle batch execution
    if request.method == 'POST' and 'execute_batch' in request.POST:
        batch_id = request.POST.get('batch_id')
        
        result = PayrollService.execute_batch(batch_id, request.user)
        
        if result['success']:
            messages.success(request, f"Batch executed! {result['count']} payments processed.")
        else:
            messages.error(request, f"Execution failed: {result['message']}")
        
        return redirect('admin_salary_management')
    
    # Handle salary update
    if request.method == 'POST' and 'update_salary' in request.POST:
        emp_id = request.POST.get('employee_id')
        employee = get_object_or_404(Employee, pk=emp_id)
        new_salary = Decimal(request.POST.get('salary'))
        reason = request.POST.get('reason', 'Salary update')
        
        history = PayrollService.update_employee_salary(
            employee=employee,
            new_salary=new_salary,
            reason=reason,
            user=request.user,
            request=request
        )
        
        if history:
            messages.success(request, f'Salary updated for {employee.user.get_full_name()}: ${history.old_salary} → ${history.new_salary}')
        else:
            messages.info(request, 'No change in salary')
        
        return redirect('admin_salary_management')
    
    # Handle bonus
    if request.method == 'POST' and 'add_bonus' in request.POST:
        emp_id = request.POST.get('employee_id')
        employee = get_object_or_404(Employee, pk=emp_id)
        amount = Decimal(request.POST.get('amount'))
        bonus_type = request.POST.get('bonus_type')
        reason = request.POST.get('reason')
        
        bonus = PayrollService.add_bonus(
            employee=employee,
            amount=amount,
            bonus_type=bonus_type,
            reason=reason,
            user=request.user,
            request=request
        )
        
        messages.success(request, f'Bonus of ${bonus.amount} added for {employee.user.get_full_name()}')
        return redirect('admin_salary_management')
    
    from .models import SalaryHistory, PayrollBatch
    employees = Employee.objects.all().select_related('user')
    month = int(request.GET.get('month', datetime.now().month))
    year = int(request.GET.get('year', datetime.now().year))
    payments = SalaryPayment.objects.filter(month=month, year=year).select_related('employee')
    bonuses = Bonus.objects.select_related('employee').all()[:10]
    history = SalaryHistory.objects.select_related('employee', 'changed_by').order_by('-changed_at')[:20]
    
    # Get pending and approved batches
    pending_batches = PayrollBatch.objects.filter(status='pending_approval').order_by('-created_at')
    approved_batches = PayrollBatch.objects.filter(status='approved').order_by('-approved_at')
    
    return render(request, 'admin/salary_management.html', {
        'employees': employees,
        'payments': payments,
        'bonuses': bonuses,
        'history': history,
        'month': month,
        'year': year,
        'pending_batches': pending_batches,
        'approved_batches': approved_batches,
    })


@login_required
@user_passes_test(is_admin)
def admin_salary_history(request, pk):
    from .models import Employee, SalaryHistory
    employee = get_object_or_404(Employee, pk=pk)
    history = SalaryHistory.objects.filter(employee=employee).order_by('-changed_at')
    return render(request, 'admin/salary_history.html', {'employee': employee, 'history': history})


@login_required
def employee_salary(request):
    from .models import SalaryHistory, Bonus, SalaryPayment
    employee = request.user.employee
    history = SalaryHistory.objects.filter(employee=employee)[:5]
    bonuses = Bonus.objects.filter(employee=employee)[:5]
    payments = SalaryPayment.objects.filter(employee=employee)[:6]
    return render(request, 'employee/salary.html', {'employee': employee, 'history': history, 'bonuses': bonuses, 'payments': payments})


@login_required
@user_passes_test(is_admin)
def payroll_reports(request):
    from .models import PayrollBatch, Department
    from django.db.models import Sum, Avg, Count
    from datetime import datetime
    
    month = int(request.GET.get('month', datetime.now().month))
    year = int(request.GET.get('year', datetime.now().year))
    dept_filter = request.GET.get('department', '')
    
    # Get summary
    payments = SalaryPayment.objects.filter(month=month, year=year, status='paid')
    if dept_filter:
        payments = payments.filter(employee__department_id=dept_filter)
    
    total_amount = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    employee_count = payments.count()
    avg_salary = payments.aggregate(Avg('amount'))['amount__avg'] or 0
    
    # Bonuses for the month
    from datetime import date
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    
    total_bonuses = Bonus.objects.filter(
        given_at__gte=start_date,
        given_at__lt=end_date
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Department breakdown
    dept_breakdown = []
    for dept in Department.objects.all():
        dept_payments = payments.filter(employee__department=dept)
        if dept_payments.exists():
            dept_breakdown.append({
                'name': dept.name,
                'employee_count': dept_payments.count(),
                'total_payroll': dept_payments.aggregate(Sum('amount'))['amount__sum'] or 0,
                'avg_salary': dept_payments.aggregate(Avg('amount'))['amount__avg'] or 0,
            })
    
    # Recent batches
    batches = PayrollBatch.objects.all()[:10]
    
    context = {
        'summary': {
            'total_amount': total_amount,
            'employee_count': employee_count,
            'avg_salary': avg_salary,
            'total_bonuses': total_bonuses,
            'month': month,
            'year': year,
        },
        'dept_breakdown': dept_breakdown,
        'batches': batches,
        'departments': Department.objects.all(),
        'month': month,
        'year': year,
    }
    
    return render(request, 'admin/payroll_reports.html', context)


@login_required
@user_passes_test(is_admin)
def payroll_export_csv(request):
    import csv
    from django.http import HttpResponse
    from datetime import datetime
    
    month = int(request.GET.get('month', datetime.now().month))
    year = int(request.GET.get('year', datetime.now().year))
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="payroll_{month}_{year}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Employee ID', 'Name', 'Department', 'Amount', 'Status', 'Payment Date', 'Transaction Ref'])
    
    payments = SalaryPayment.objects.filter(
        month=month,
        year=year
    ).select_related('employee', 'employee__department')
    
    for payment in payments:
        writer.writerow([
            payment.employee.employee_id,
            payment.employee.user.get_full_name(),
            payment.employee.department.name if payment.employee.department else 'N/A',
            float(payment.amount),
            payment.status,
            payment.payment_date.strftime('%Y-%m-%d %H:%M') if payment.payment_date else 'N/A',
            payment.transaction_reference,
        ])
    
    return response



