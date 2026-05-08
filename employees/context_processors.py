from .models import Leave, AttendanceCorrection, PasswordResetRequest


def notifications(request):
    """Add notification counts to all templates"""
    context = {
        'pending_count': 0,
        'leave_count': 0,
        'correction_count': 0,
        'password_reset_count': 0,
    }
    
    if request.user.is_authenticated and request.user.is_staff:
        leave_count = Leave.objects.filter(status='pending').count()
        correction_count = AttendanceCorrection.objects.filter(status='pending').count()
        password_reset_count = PasswordResetRequest.objects.filter(status='pending').count()
        
        context.update({
            'leave_count': leave_count,
            'correction_count': correction_count,
            'password_reset_count': password_reset_count,
            'pending_count': leave_count + correction_count + password_reset_count,
        })
    
    return context
