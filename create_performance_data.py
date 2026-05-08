#!/usr/bin/env python
"""
Script to create sample performance management data
"""
import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import *

def create_sample_performance_data():
    print("Creating sample performance management data...")
    
    # Create some KPIs
    kpis_data = [
        {
            'name': 'Sales Target Achievement',
            'description': 'Monthly sales target achievement percentage',
            'target_value': 100,
            'unit': '%',
            'weight': 2.0
        },
        {
            'name': 'Customer Satisfaction Score',
            'description': 'Average customer satisfaction rating',
            'target_value': 4.5,
            'unit': 'rating',
            'weight': 1.5
        },
        {
            'name': 'Project Completion Rate',
            'description': 'Percentage of projects completed on time',
            'target_value': 95,
            'unit': '%',
            'weight': 1.8
        },
        {
            'name': 'Training Hours Completed',
            'description': 'Number of training hours completed per quarter',
            'target_value': 40,
            'unit': 'hours',
            'weight': 1.0
        }
    ]
    
    for kpi_data in kpis_data:
        kpi, created = KPI.objects.get_or_create(
            name=kpi_data['name'],
            defaults=kpi_data
        )
        if created:
            print(f"Created KPI: {kpi.name}")
    
    # Get some employees
    employees = Employee.objects.all()[:5]  # Get first 5 employees
    
    if not employees:
        print("No employees found. Please create some employees first.")
        return
    
    # Create performance reviews
    for i, employee in enumerate(employees):
        review_data = {
            'employee': employee,
            'reviewer': employees[0],  # First employee as reviewer (admin)
            'review_type': 'quarterly',
            'review_period_start': date.today() - timedelta(days=90),
            'review_period_end': date.today(),
            'overall_rating': Decimal(str(3.5 + (i * 0.3))),  # Varying ratings
            'goals_achievement': Decimal(str(75 + (i * 5))),  # 75%, 80%, 85%, etc.
            'attendance_score': Decimal('4.2'),
            'quality_of_work': Decimal('4.0'),
            'achievements': f'Successfully completed {3 + i} major projects and exceeded expectations in client communication.',
            'areas_of_improvement': 'Could improve time management and technical documentation skills.',
            'development_plan': 'Enroll in advanced project management course and technical writing workshop.',
            'manager_comments': 'Shows great potential and dedication to work.',
            'status': 'approved'
        }
        
        review, created = PerformanceReview.objects.get_or_create(
            employee=employee,
            review_period_start=review_data['review_period_start'],
            review_period_end=review_data['review_period_end'],
            defaults=review_data
        )
        if created:
            print(f"Created performance review for: {employee.user.get_full_name()}")
    
    # Create performance goals
    goals_data = [
        {
            'title': 'Increase Sales by 20%',
            'description': 'Achieve 20% increase in monthly sales compared to previous quarter',
            'target_value': 120,
            'unit': '%',
            'priority': 'high',
            'start_date': date.today(),
            'due_date': date.today() + timedelta(days=90)
        },
        {
            'title': 'Complete Advanced Training',
            'description': 'Complete advanced technical training certification',
            'target_value': 1,
            'unit': 'certification',
            'priority': 'medium',
            'start_date': date.today(),
            'due_date': date.today() + timedelta(days=60)
        },
        {
            'title': 'Improve Customer Ratings',
            'description': 'Achieve average customer rating of 4.5 or higher',
            'target_value': 4.5,
            'unit': 'rating',
            'priority': 'high',
            'start_date': date.today(),
            'due_date': date.today() + timedelta(days=120)
        }
    ]
    
    admin_user = User.objects.filter(is_staff=True).first()
    
    for i, employee in enumerate(employees[:3]):  # Create goals for first 3 employees
        goal_data = goals_data[i].copy()
        goal_data['employee'] = employee
        goal_data['created_by'] = admin_user
        goal_data['current_value'] = Decimal(str(goal_data['target_value'] * 0.6))  # 60% progress
        
        goal, created = PerformanceGoal.objects.get_or_create(
            employee=employee,
            title=goal_data['title'],
            defaults=goal_data
        )
        if created:
            print(f"Created performance goal for {employee.user.get_full_name()}: {goal.title}")
    
    # Assign KPIs to employees
    kpis = KPI.objects.all()
    for i, employee in enumerate(employees):
        for j, kpi in enumerate(kpis):
            if j <= i:  # Assign different number of KPIs to different employees
                emp_kpi_data = {
                    'employee': employee,
                    'kpi': kpi,
                    'target_value': kpi.target_value,
                    'current_value': kpi.target_value * Decimal('0.7'),  # 70% achievement
                    'period_start': date.today() - timedelta(days=30),
                    'period_end': date.today() + timedelta(days=60)
                }
                
                emp_kpi, created = EmployeeKPI.objects.get_or_create(
                    employee=employee,
                    kpi=kpi,
                    period_start=emp_kpi_data['period_start'],
                    defaults=emp_kpi_data
                )
                if created:
                    print(f"Assigned KPI '{kpi.name}' to {employee.user.get_full_name()}")
    
    # Create some employee feedback
    for i, employee in enumerate(employees[1:]):  # Skip first employee
        feedback_data = {
            'employee': employee,
            'feedback_by': employees[0],  # First employee gives feedback
            'feedback_type': 'manager',
            'communication_rating': 4,
            'teamwork_rating': 4,
            'technical_skills_rating': 3 + (i % 2),
            'leadership_rating': 3,
            'problem_solving_rating': 4,
            'strengths': 'Excellent communication skills and team collaboration. Shows initiative in problem-solving.',
            'areas_for_improvement': 'Could improve technical documentation and time management skills.',
            'additional_comments': 'Overall a valuable team member with great potential for growth.',
            'is_anonymous': False
        }
        
        feedback, created = EmployeeFeedback.objects.get_or_create(
            employee=employee,
            feedback_by=employees[0],
            feedback_type='manager',
            defaults=feedback_data
        )
        if created:
            print(f"Created feedback for: {employee.user.get_full_name()}")
    
    print("\nSample performance management data created successfully!")
    print("\nSummary:")
    print(f"- KPIs: {KPI.objects.count()}")
    print(f"- Performance Reviews: {PerformanceReview.objects.count()}")
    print(f"- Performance Goals: {PerformanceGoal.objects.count()}")
    print(f"- Employee KPIs: {EmployeeKPI.objects.count()}")
    print(f"- Employee Feedback: {EmployeeFeedback.objects.count()}")

if __name__ == '__main__':
    create_sample_performance_data()