# FEEDBACK SYSTEM VIEWS

@login_required
@user_passes_test(is_admin)
def feedback_list(request):
    """Admin view all feedback"""
    feedback = EmployeeFeedback.objects.select_related('employee__user', 'feedback_by__user').order_by('-created_at')
    return render(request, 'admin/feedback_list.html', {'feedback': feedback})


@login_required
def employee_feedback_give(request):
    """Employee give feedback to others"""
    try:
        employee = request.user.employee
        
        if request.method == 'POST':
            form = EmployeeFeedbackForm(request.POST)
            if form.is_valid():
                feedback = form.save(commit=False)
                feedback.feedback_by = employee
                feedback.save()
                messages.success(request, 'Feedback submitted successfully!')
                return redirect('employee_feedback_given')
        else:
            form = EmployeeFeedbackForm()
            form.fields['employee'].queryset = Employee.objects.exclude(pk=employee.pk)
        
        return render(request, 'employee/feedback_form.html', {'form': form})
        
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found!')
        return redirect('employee_dashboard')


@login_required
def employee_feedback_received(request):
    """Employee view received feedback"""
    try:
        employee = request.user.employee
        feedback = EmployeeFeedback.objects.filter(employee=employee).select_related('feedback_by__user').order_by('-created_at')
        return render(request, 'employee/feedback_received.html', {'feedback': feedback})
        
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found!')
        return redirect('employee_dashboard')


@login_required
def employee_feedback_given(request):
    """Employee view given feedback"""
    try:
        employee = request.user.employee
        feedback = EmployeeFeedback.objects.filter(feedback_by=employee).select_related('employee__user').order_by('-created_at')
        return render(request, 'employee/feedback_given.html', {'feedback': feedback})
        
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found!')
        return redirect('employee_dashboard')