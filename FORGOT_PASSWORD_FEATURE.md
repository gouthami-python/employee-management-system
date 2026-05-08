# Forgot Password Feature

## Overview
Employees can now request password reset by providing their new password. Admin reviews and approves/rejects the request.

## Features

### For Employees:
1. **Forgot Password Link**: Available on employee login page
2. **Submit Request**: Enter username, reason, and new password
3. **Track Status**: View all password reset requests and their status
4. **Sidebar Access**: "Password Reset Status" link in employee menu

### For Admin:
1. **Review Requests**: View all pending password reset requests
2. **Approve/Reject**: Review employee details and reason
3. **Auto-Update**: When approved, password is automatically changed to employee's new password
4. **Add Remarks**: Optional admin remarks for each decision
5. **Sidebar Access**: "Password Reset Requests" link in admin menu

## URLs

### Public URL:
- `/forgot-password/` - Forgot password request form (no login required)

### Employee URLs:
- `/password-reset/status/` - View all password reset requests status

### Admin URLs:
- `/admin-panel/password-reset/` - View pending password reset requests
- `/admin-panel/password-reset/<id>/review/` - Review specific request

## Database
- **Model**: `PasswordResetRequest`
- **Fields**: employee, reason, new_password, status, requested_at, reviewed_by, reviewed_at, admin_remarks

## How It Works

1. **Employee Side**:
   - Employee forgets password
   - Clicks "Forgot Password?" on login page
   - Enters username, reason, and new password (with confirmation)
   - Submits request
   - Can track status in dashboard under "Password Reset Status"

2. **Admin Side**:
   - Receives notification in "Password Reset Requests" menu
   - Reviews employee's reason and details
   - Approves (changes password to employee's new password) or Rejects with remarks
   - Employee gets updated status

## Security Notes
- Password is stored temporarily in the database (not hashed until approved)
- Only admin can approve password changes
- Employee must provide reason for password reset
- All requests are tracked with timestamps

## Migration
- Migration file: `0008_alter_passwordresetrequest_options_and_more.py`
- Already applied to database
