from django.contrib import admin
from .models import *


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'head', 'created_at']
    search_fields = ['name']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['title', 'level']
    search_fields = ['title']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'user', 'department', 'role', 'is_manager']
    list_filter = ['department', 'role', 'is_manager']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'assigned_to', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority', 'department']
    search_fields = ['title', 'assigned_to__user__first_name']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'department', 'is_active', 'created_at']
    list_filter = ['is_active', 'department']


@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'status']
    list_filter = ['status', 'leave_type']
    search_fields = ['employee__user__first_name']


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['subject', 'employee', 'status', 'is_anonymous', 'created_at']
    list_filter = ['status', 'is_anonymous']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['employee', 'reviewer', 'rating', 'created_at']
    list_filter = ['rating']


@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'status', 'requested_at', 'reviewed_by']
    list_filter = ['status', 'requested_at']
    search_fields = ['employee__user__first_name', 'employee__user__last_name']


@admin.register(AttendanceCorrection)
class AttendanceCorrectionAdmin(admin.ModelAdmin):
    list_display = ['employee', 'attendance', 'status', 'requested_at', 'reviewed_by']
    list_filter = ['status', 'requested_at']
    search_fields = ['employee__user__first_name', 'employee__user__last_name']