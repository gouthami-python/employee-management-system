"""
Production-ready Payroll Service
Handles salary payments with idempotency, atomicity, and audit trails
"""
import uuid
from decimal import Decimal
from datetime import datetime
from django.db import transaction, IntegrityError
from django.utils import timezone
from .models import Employee, SalaryPayment, PayrollBatch, SalaryHistory, Bonus


def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


def get_user_agent(request):
    """Extract user agent from request"""
    return request.META.get('HTTP_USER_AGENT', '')[:500]


class PayrollService:
    """Service for managing payroll operations"""
    
    @staticmethod
    def generate_idempotency_key(employee_id, month, year, batch_id=None):
        """Generate unique idempotency key"""
        if batch_id:
            return f"batch-{batch_id}-emp-{employee_id}-{month}-{year}"
        return f"emp-{employee_id}-{month}-{year}-{uuid.uuid4().hex[:8]}"
    
    @staticmethod
    def create_batch(month, year, user, remarks=''):
        """Create a new payroll batch"""
        batch_id = f"BATCH-{year}{month:02d}-{uuid.uuid4().hex[:8].upper()}"
        batch = PayrollBatch.objects.create(
            batch_id=batch_id,
            month=month,
            year=year,
            status='draft',
            created_by=user,
            remarks=remarks
        )
        return batch
    
    @staticmethod
    @transaction.atomic
    def process_bulk_payment(employee_ids, month, year, user, request, batch=None, auto_approve=False, approval_threshold=10000):
        """
        Process bulk salary payments with atomicity and idempotency
        Returns: dict with success, failed, and skipped employee details
        """
        results = {
            'successful': [],
            'failed': [],
            'skipped': [],
            'batch': None
        }
        
        # Create batch if not provided
        if not batch:
            batch = PayrollService.create_batch(month, year, user, f"Bulk payment for {month}/{year}")
        
        results['batch'] = batch
        
        # Check if approval needed
        total_estimate = sum(Employee.objects.filter(id__in=employee_ids).values_list('salary', flat=True))
        if total_estimate >= approval_threshold and not auto_approve:
            batch.requires_approval = True
            batch.status = 'pending_approval'
        else:
            batch.status = 'processing'
        
        batch.approval_threshold = approval_threshold
        batch.save()
        
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        total_amount = Decimal('0.00')
        successful_count = 0
        failed_count = 0
        
        for emp_id in employee_ids:
            try:
                employee = Employee.objects.select_for_update().get(pk=emp_id)
                
                # Check if already paid
                existing = SalaryPayment.objects.filter(
                    employee=employee,
                    month=month,
                    year=year
                ).first()
                
                if existing:
                    results['skipped'].append({
                        'employee': employee,
                        'reason': f'Already paid on {existing.payment_date or existing.created_at}'
                    })
                    continue
                
                # Validate salary
                if not employee.salary or employee.salary <= 0:
                    results['failed'].append({
                        'employee': employee,
                        'reason': 'Invalid or zero salary'
                    })
                    failed_count += 1
                    continue
                
                # Generate idempotency key
                idempotency_key = PayrollService.generate_idempotency_key(
                    employee.id, month, year, batch.batch_id
                )
                
                # Determine payment status
                if batch.requires_approval:
                    payment_status = 'pending_approval'
                elif auto_approve:
                    payment_status = 'paid'
                else:
                    payment_status = 'approved'
                
                # Create payment
                payment = SalaryPayment.objects.create(
                    batch=batch,
                    employee=employee,
                    amount=employee.salary,
                    month=month,
                    year=year,
                    status=payment_status,
                    idempotency_key=idempotency_key,
                    transaction_reference=f"TXN-{uuid.uuid4().hex[:12].upper()}",
                    created_by=user,
                    created_at=timezone.now(),
                    paid_by=user if auto_approve else None,
                    payment_date=timezone.now() if auto_approve else None,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                
                results['successful'].append({
                    'employee': employee,
                    'payment': payment,
                    'amount': employee.salary
                })
                
                total_amount += employee.salary
                successful_count += 1
                
            except IntegrityError as e:
                results['failed'].append({
                    'employee': Employee.objects.get(pk=emp_id),
                    'reason': f'Duplicate payment detected: {str(e)}'
                })
                failed_count += 1
                
            except Employee.DoesNotExist:
                results['failed'].append({
                    'employee_id': emp_id,
                    'reason': 'Employee not found'
                })
                failed_count += 1
                
            except Exception as e:
                results['failed'].append({
                    'employee': Employee.objects.get(pk=emp_id),
                    'reason': str(e)
                })
                failed_count += 1
        
        # Update batch
        batch.total_amount = total_amount
        batch.employee_count = len(employee_ids)
        batch.successful_count = successful_count
        batch.failed_count = failed_count
        batch.status = 'completed' if failed_count == 0 else 'failed'
        batch.processed_by = user
        batch.processed_at = timezone.now()
        batch.save()
        
        return results
    
    @staticmethod
    @transaction.atomic
    def update_employee_salary(employee, new_salary, reason, user, request):
        """Update employee salary with history tracking"""
        old_salary = employee.salary or Decimal('0.00')
        
        if old_salary == new_salary:
            return None
        
        # Determine change type
        if new_salary > old_salary:
            change_type = 'increment'
        elif new_salary < old_salary:
            change_type = 'decrement'
        else:
            change_type = 'adjustment'
        
        # Create history record
        history = SalaryHistory.objects.create(
            employee=employee,
            old_salary=old_salary,
            new_salary=new_salary,
            change_type=change_type,
            reason=reason,
            changed_by=user,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        
        # Update employee salary
        employee.salary = new_salary
        employee.save(update_fields=['salary'])
        
        return history
    
    @staticmethod
    @transaction.atomic
    def add_bonus(employee, amount, bonus_type, reason, user, request):
        """Add bonus to employee"""
        bonus = Bonus.objects.create(
            employee=employee,
            amount=amount,
            bonus_type=bonus_type,
            reason=reason,
            given_by=user,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        return bonus
    
    @staticmethod
    def get_payment_summary(month, year):
        """Get payment summary for a month"""
        payments = SalaryPayment.objects.filter(
            month=month,
            year=year,
            status='paid'
        ).select_related('employee', 'created_by')
        
        total_amount = sum(p.amount for p in payments)
        employee_count = payments.count()
        
        return {
            'payments': payments,
            'total_amount': total_amount,
            'employee_count': employee_count,
            'month': month,
            'year': year
        }
    
    @staticmethod
    @transaction.atomic
    def approve_batch(batch_id, user, remarks=''):
        """Approve a pending batch"""
        try:
            batch = PayrollBatch.objects.select_for_update().get(pk=batch_id)
            
            if batch.status != 'pending_approval':
                return {'success': False, 'message': 'Batch not pending approval'}
            
            # Update batch
            batch.status = 'approved'
            batch.approved_by = user
            batch.approved_at = timezone.now()
            batch.remarks = remarks
            batch.save()
            
            # Update payments
            SalaryPayment.objects.filter(batch=batch, status='pending_approval').update(
                status='approved',
                approved_by=user,
                approved_at=timezone.now()
            )
            
            return {'success': True, 'batch': batch}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    @transaction.atomic
    def execute_batch(batch_id, user):
        """Execute approved batch (mark as paid)"""
        try:
            batch = PayrollBatch.objects.select_for_update().get(pk=batch_id)
            
            if batch.status != 'approved':
                return {'success': False, 'message': 'Batch not approved'}
            
            # Update batch
            batch.status = 'processing'
            batch.processed_by = user
            batch.processed_at = timezone.now()
            batch.save()
            
            # Update payments
            payments = SalaryPayment.objects.filter(batch=batch, status='approved')
            for payment in payments:
                payment.status = 'paid'
                payment.paid_by = user
                payment.payment_date = timezone.now()
                payment.save()
            
            # Mark batch complete
            batch.status = 'completed'
            batch.save()
            
            return {'success': True, 'batch': batch, 'count': payments.count()}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def retry_failed_payment(payment_id, user, request):
        """Retry a failed payment"""
        try:
            with transaction.atomic():
                payment = SalaryPayment.objects.select_for_update().get(pk=payment_id)
                
                if payment.status == 'paid':
                    return {'success': False, 'message': 'Payment already completed'}
                
                payment.status = 'paid'
                payment.paid_by = user
                payment.payment_date = timezone.now()
                payment.error_message = ''
                payment.save()
                
                return {'success': True, 'payment': payment}
                
        except Exception as e:
            return {'success': False, 'message': str(e)}
