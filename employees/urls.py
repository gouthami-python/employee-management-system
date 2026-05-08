from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # Authentication URLs
    path('admin-login/', views.admin_login, name='admin_login'),
    path('employee-login/', views.employee_login, name='employee_login'),
    path('employee-register/', views.employee_register, name='employee_register'),
    path('forgot-password/', views.employee_forgot_password, name='employee_forgot_password'),
    path('logout/', views.logout_view, name='logout'),

    # Admin URLs
    path('admin-panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/profile/', views.admin_profile, name='admin_profile'),
    path('admin-panel/employees/', views.employee_list, name='employee_list'),
    path('admin-panel/employees/add/', views.employee_add, name='employee_add'),
    path('admin-panel/employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('admin-panel/employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    path('admin-panel/departments/', views.department_list, name='department_list'),
    path('admin-panel/departments/add/', views.department_add, name='department_add'),
    path('admin-panel/departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('admin-panel/departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
    path('admin-panel/tasks/', views.task_list, name='task_list'),
    path('admin-panel/tasks/assign/', views.task_assign, name='task_assign'),
    path('admin-panel/tasks/<int:pk>/update/', views.task_update_status, name='task_update_status'),
    path('admin-panel/announcements/', views.announcement_list, name='announcement_list'),
    path('admin-panel/announcements/add/', views.announcement_add, name='announcement_add'),
    path('admin-panel/announcements/<int:pk>/delete/', views.announcement_delete, name='announcement_delete'),
    path('admin-panel/leaves/', views.leave_requests, name='leave_requests'),
    path('admin-panel/leaves/<int:pk>/approve/', views.leave_approve, name='leave_approve'),
    path('admin-panel/leaves/<int:pk>/reject/', views.leave_reject, name='leave_reject'),
    path('admin-panel/complaints/', views.complaint_list, name='complaint_list'),
    path('admin-panel/complaints/<int:pk>/respond/', views.complaint_respond, name='complaint_respond'),
    path('admin-panel/reviews/', views.review_list, name='review_list'),
    path('admin-panel/reviews/add/', views.review_add, name='review_add'),
    path('admin-panel/attendance/', views.admin_attendance_list, name='admin_attendance_list'),
    path('admin-panel/attendance/report/', views.admin_attendance_report, name='admin_attendance_report'),
    path('admin-panel/attendance/corrections/', views.admin_correction_list, name='admin_correction_list'),
    path('admin-panel/attendance/corrections/<int:pk>/review/', views.admin_correction_review, name='admin_correction_review'),
    path('admin-panel/password-reset/', views.admin_password_reset_list, name='admin_password_reset_list'),
    path('admin-panel/password-reset/<int:pk>/review/', views.admin_password_reset_review, name='admin_password_reset_review'),
    path('admin-panel/salary/', views.admin_salary_management, name='admin_salary_management'),
    path('admin-panel/salary/<int:pk>/history/', views.admin_salary_history, name='admin_salary_history'),
    path('admin-panel/payroll/reports/', views.payroll_reports, name='payroll_reports'),
    path('admin-panel/payroll/export-csv/', views.payroll_export_csv, name='payroll_export_csv'),
    
    # Employee URLs
    path('dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('attendance/', views.employee_attendance, name='employee_attendance'),
    path('attendance/<int:pk>/correction/', views.employee_attendance_correction, name='employee_attendance_correction'),
    path('attendance/corrections/', views.employee_correction_status, name='employee_correction_status'),
    path('password-reset/status/', views.employee_password_reset_status, name='employee_password_reset_status'),
    path('tasks/', views.employee_tasks, name='employee_tasks'),
    path('tasks/<int:pk>/update/', views.employee_task_update, name='employee_task_update'),
    path('leave/apply/', views.employee_leave_apply, name='employee_leave_apply'),
    path('leave/status/', views.employee_leave_status, name='employee_leave_status'),
    path('complaint/submit/', views.employee_complaint_submit, name='employee_complaint_submit'),
    path('complaint/track/', views.employee_complaint_track, name='employee_complaint_track'),
    path('profile/', views.employee_profile, name='employee_profile'),
    path('feedback/submit/', views.employee_feedback_submit, name='employee_feedback_submit'),
    path('salary/', views.employee_salary, name='employee_salary'),
    path('toggle-theme/', views.toggle_theme, name='toggle_theme'),
    
    # Job/Hiring URLs
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:pk>/apply/', views.job_apply, name='job_apply'),
    path('application-status/', views.application_status, name='application_status'),
    path('admin-panel/vacancies/', views.vacancy_list, name='vacancy_list'),
    path('admin-panel/vacancies/add/', views.vacancy_add, name='vacancy_add'),
    path('admin-panel/applications/', views.application_list, name='application_list'),
    path('admin-panel/applications/<int:pk>/update/', views.application_update, name='application_update'),
    
    # Note: Attendance and Salary URLs temporarily commented out until views are implemented
    # Uncomment these when the corresponding views are added to views.py
    

]