# ATTENDANCE VIEWS
@login_required
def employee_attendance(request):
    try:
        employee = request.user.employee
        today = date.today()
        today_attendance = AttendanceRecord.objects.filter(employee=employee, date=today).first()
        recent_records = AttendanceRecord.objects.filter(employee=employee).order_by('-date')[:10]
        return render(request, 'employee/attendance.html', {
            'employee': employee, 'today_attendance': today_attendance, 'recent_records': recent_records, 'today': today
        })
    except Employee.DoesNotExist:
        return redirect('employee_dashboard')

@login_required
def employee_check_in(request):
    if request.method == 'POST':
        try:
            employee = request.user.employee
            today = date.today()
            current_time = timezone.now().time()
            existing_record = AttendanceRecord.objects.filter(employee=employee, date=today).first()
            if existing_record and existing_record.check_in_time:
                return JsonResponse({'success': False, 'message': 'Already checked in!'})
            if existing_record:
                existing_record.check_in_time = current_time
                existing_record.status = 'present'
                existing_record.save()
            else:
                AttendanceRecord.objects.create(employee=employee, date=today, check_in_time=current_time, status='present')
            return JsonResponse({'success': True, 'message': f'Checked in at {current_time.strftime("%H:%M")}'})
        except:
            return JsonResponse({'success': False, 'message': 'Error'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def employee_check_out(request):
    if request.method == 'POST':
        try:
            employee = request.user.employee
            today = date.today()
            current_time = timezone.now().time()
            record = AttendanceRecord.objects.filter(employee=employee, date=today).first()
            if not record or not record.check_in_time:
                return JsonResponse({'success': False, 'message': 'Check in first!'})
            if record.check_out_time:
                return JsonResponse({'success': False, 'message': 'Already checked out!'})
            record.check_out_time = current_time
            check_in_datetime = datetime.combine(today, record.check_in_time)
            check_out_datetime = datetime.combine(today, current_time)
            total_seconds = (check_out_datetime - check_in_datetime).total_seconds()
            record.total_hours = Decimal(str(total_seconds / 3600)).quantize(Decimal('0.01'))
            record.save()
            return JsonResponse({'success': True, 'message': f'Checked out at {current_time.strftime("%H:%M")}'})
        except:
            return JsonResponse({'success': False, 'message': 'Error'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
def attendance_correction_request(request):
    try:
        employee = request.user.employee
        if request.method == 'POST':
            form = AttendanceCorrectionForm(request.POST)
            if form.is_valid():
                correction = form.save(commit=False)
                correction.employee = employee
                correction.save()
                messages.success(request, 'Correction request submitted!')
                return redirect('employee_attendance')
        else:
            form = AttendanceCorrectionForm()
        return render(request, 'employee/attendance_correction.html', {'form': form})
    except:
        return redirect('employee_dashboard')

@login_required
@user_passes_test(is_admin)
def admin_attendance_dashboard(request):
    today = date.today()
    today_records = AttendanceRecord.objects.filter(date=today)
    total_employees = Employee.objects.count()
    present_today = today_records.filter(status='present').count()
    absent_today = total_employees - today_records.count()
    return render(request, 'admin/attendance_dashboard.html', {
        'total_employees': total_employees, 'present_today': present_today, 'absent_today': absent_today, 'today': today
    })

@login_required
@user_passes_test(is_admin)
def admin_attendance_records(request):
    records = AttendanceRecord.objects.select_related('employee__user').order_by('-date')
    employees = Employee.objects.select_related('user').all()
    return render(request, 'admin/attendance_records.html', {'records': records, 'employees': employees})

@login_required
@user_passes_test(is_admin)
def admin_correction_requests(request):
    corrections = AttendanceCorrection.objects.select_related('employee__user').order_by('-requested_at')
    return render(request, 'admin/correction_requests.html', {'corrections': corrections})

@login_required
@user_passes_test(is_admin)
def admin_correction_approve(request, pk):
    correction = get_object_or_404(AttendanceCorrection, pk=pk)
    correction.status = 'approved'
    correction.reviewed_by = request.user
    correction.reviewed_at = timezone.now()
    correction.save()
    messages.success(request, 'Correction approved!')
    return redirect('admin_correction_requests')

@login_required
@user_passes_test(is_admin)
def admin_correction_reject(request, pk):
    correction = get_object_or_404(AttendanceCorrection, pk=pk)
    correction.status = 'rejected'
    correction.reviewed_by = request.user
    correction.reviewed_at = timezone.now()
    correction.save()
    messages.success(request, 'Correction rejected!')
    return redirect('admin_correction_requests')

@login_required
@user_passes_test(is_admin)
def admin_work_schedules(request):
    schedules = WorkSchedule.objects.select_related('employee__user').order_by('employee__employee_id')
    return render(request, 'admin/work_schedules.html', {'schedules': schedules})

@login_required
@user_passes_test(is_admin)
def admin_schedule_add(request):
    if request.method == 'POST':
        form = WorkScheduleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Schedule added!')
            return redirect('admin_work_schedules')
    else:
        form = WorkScheduleForm()
    return render(request, 'admin/schedule_form.html', {'form': form})

# SALARY VIEWS
@login_required
@user_passes_test(is_admin)
def admin_salary_list(request):
    records = SalaryRecord.objects.select_related('employee__user').order_by('-year', '-month')
    employees = Employee.objects.select_related('user').all()
    return render(request, 'admin/salary_list.html', {
        'records': records, 'employees': employees, 'months': [(i, i) for i in range(1, 13)], 'years': [(i, i) for i in range(2020, 2031)]
    })

@login_required
@user_passes_test(is_admin)
def admin_salary_structure_list(request):
    structures = SalaryStructure.objects.select_related('employee__user').filter(is_active=True)
    return render(request, 'admin/salary_structure_list.html', {'structures': structures})

@login_required
@user_passes_test(is_admin)
def admin_salary_structure_add(request):
    if request.method == 'POST':
        form = SalaryStructureForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salary structure added!')
            return redirect('admin_salary_structure_list')
    else:
        form = SalaryStructureForm()
    return render(request, 'admin/salary_structure_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def admin_salary_generate(request):
    if request.method == 'POST':
        form = SalaryRecordForm(request.POST)
        if form.is_valid():
            employee = form.cleaned_data['employee']
            month = form.cleaned_data['month']
            year = form.cleaned_data['year']
            if SalaryRecord.objects.filter(employee=employee, month=month, year=year).exists():
                messages.error(request, 'Salary already exists')
            else:
                try:
                    structure = SalaryStructure.objects.get(employee=employee, is_active=True)
                    SalaryRecord.objects.create(
                        employee=employee, salary_structure=structure, month=month, year=year,
                        basic_pay=structure.basic_pay, hra=structure.hra, transport_allowance=structure.transport_allowance,
                        medical_allowance=structure.medical_allowance, other_allowances=structure.other_allowances,
                        bonus=form.cleaned_data['bonus'], overtime=form.cleaned_data['overtime'],
                        pf_employee=(structure.basic_pay * structure.pf_rate / 100),
                        pf_employer=(structure.basic_pay * structure.pf_rate / 100),
                        esi_employee=(structure.gross_salary * structure.esi_rate / 100),
                        esi_employer=(structure.gross_salary * 3.25 / 100),
                        professional_tax=structure.pt_amount, income_tax=form.cleaned_data['income_tax'],
                        other_deductions=form.cleaned_data['other_deductions'], generated_by=request.user
                    )
                    messages.success(request, 'Salary generated!')
                    return redirect('admin_salary_list')
                except:
                    messages.error(request, 'No salary structure found')
    else:
        form = SalaryRecordForm()
    return render(request, 'admin/salary_generate.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def admin_salary_mark_paid(request, pk):
    salary_record = get_object_or_404(SalaryRecord, pk=pk)
    salary_record.status = 'paid'
    salary_record.paid_at = timezone.now()
    salary_record.save()
    messages.success(request, 'Salary marked as paid!')
    return redirect('admin_salary_list')

@login_required
def employee_salary_list(request):
    try:
        employee = request.user.employee
        records = SalaryRecord.objects.filter(employee=employee).order_by('-year', '-month')
        return render(request, 'employee/salary_list.html', {'records': records, 'employee': employee})
    except:
        return redirect('employee_dashboard')

@login_required
def employee_salary_detail(request, pk):
    try:
        employee = request.user.employee
        salary_record = get_object_or_404(SalaryRecord, pk=pk, employee=employee)
        return render(request, 'employee/salary_detail.html', {'salary_record': salary_record, 'employee': employee})
    except:
        return redirect('employee_dashboard')

@login_required
def salary_slip_pdf(request, pk):
    try:
        if request.user.is_staff:
            salary_record = get_object_or_404(SalaryRecord, pk=pk)
        else:
            employee = request.user.employee
            salary_record = get_object_or_404(SalaryRecord, pk=pk, employee=employee)
        
        from django.http import HttpResponse
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="salary_slip_{salary_record.employee.employee_id}.pdf"'
        
        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter
        
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 50, "TechCorp Solutions")
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 70, "Salary Slip")
        
        y = height - 120
        p.setFont("Helvetica-Bold", 10)
        p.drawString(50, y, f"Employee: {salary_record.employee.user.get_full_name()}")
        p.drawString(300, y, f"Employee ID: {salary_record.employee.employee_id}")
        
        y -= 20
        p.drawString(50, y, f"Month/Year: {salary_record.month_name} {salary_record.year}")
        
        y -= 40
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "EARNINGS")
        p.drawString(400, y, "DEDUCTIONS")
        
        y -= 20
        p.setFont("Helvetica", 10)
        earnings = [("Basic Pay", salary_record.basic_pay), ("HRA", salary_record.hra), ("Bonus", salary_record.bonus)]
        deductions = [("PF", salary_record.pf_employee), ("ESI", salary_record.esi_employee), ("Tax", salary_record.income_tax)]
        
        for i, (label, amount) in enumerate(earnings):
            p.drawString(50, y - i*15, f"{label}: {amount}")
        
        for i, (label, amount) in enumerate(deductions):
            p.drawString(400, y - i*15, f"{label}: {amount}")
        
        y -= 80
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, f"NET SALARY: {salary_record.net_salary}")
        
        p.showPage()
        p.save()
        return response
    except:
        return redirect('employee_dashboard')