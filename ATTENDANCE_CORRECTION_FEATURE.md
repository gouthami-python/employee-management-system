# Attendance Correction Feature

## Overview
Employees can now request corrections if they accidentally checked out or need to modify their attendance records.

## Features

### For Employees:
1. **Request Correction**: Click "Request Correction" button next to any checked-out attendance record
2. **View Status**: Track all correction requests and their status (Pending/Approved/Rejected)
3. **Quick Access**: New sidebar link "Correction Requests" for easy navigation

### For Admin:
1. **Review Requests**: View all pending correction requests in one place
2. **Approve/Reject**: Review each request with employee details and reason
3. **Auto-Update**: When approved, checkout time is automatically removed
4. **Add Remarks**: Optional admin remarks for each decision
5. **Quick Access**: New sidebar link "Correction Requests"

## URLs

### Employee URLs:
- `/attendance/<id>/correction/` - Request correction for specific attendance
- `/attendance/corrections/` - View all correction requests status

### Admin URLs:
- `/admin-panel/attendance/corrections/` - View pending correction requests
- `/admin-panel/attendance/corrections/<id>/review/` - Review specific request

## Database
- **Model**: `AttendanceCorrection`
- **Fields**: employee, attendance, reason, status, requested_at, reviewed_by, reviewed_at, admin_remarks

## How It Works

1. **Employee Side**:
   - Employee checks out by mistake
   - Clicks "Request Correction" button on attendance history
   - Fills reason and submits request
   - Tracks status in "Correction Requests" page

2. **Admin Side**:
   - Receives notification in "Correction Requests" menu
   - Reviews employee's reason and attendance details
   - Approves (removes checkout) or Rejects with remarks
   - Employee gets updated status

## Migration
- Migration file: `0007_attendancecorrection.py`
- Already applied to database
