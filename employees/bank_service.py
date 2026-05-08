"""
Bank Integration Service
Handles bank account verification, file generation, and reconciliation
"""
import hashlib
import uuid
from decimal import Decimal
from datetime import datetime, date
from django.db import transaction
from django.utils import timezone
from .bank_models import BankAccount, BankTransaction, BankSubmissionFile, ReconciliationException
from .models import SalaryPayment, PayrollBatch
import csv
import io


class BankService:
    """Service for bank operations"""
    
    @staticmethod
    def verify_bank_account(bank_account, method='manual', proof=''):
        """Verify bank account"""
        bank_account.verification_status = 'verified'
        bank_account.verification_date = timezone.now()
        bank_account.verification_method = method
        bank_account.verification_proof = proof
        bank_account.save()
        return bank_account
    
    @staticmethod
    def initiate_micro_deposit(bank_account):
        """Initiate micro-deposit verification (placeholder)"""
        # In production: integrate with bank API to send small amounts
        bank_account.verification_status = 'pending'
        bank_account.save()
        return {'status': 'pending', 'message': 'Micro-deposit initiated'}
    
    @staticmethod
    @transaction.atomic
    def prepare_bank_transactions(batch):
        """Create bank transactions for approved batch"""
        transactions = []
        
        payments = SalaryPayment.objects.filter(
            batch=batch,
            status='approved'
        ).select_related('employee', 'employee__bank_account')
        
        for payment in payments:
            # Check bank account
            if not hasattr(payment.employee, 'bank_account'):
                payment.status = 'failed'
                payment.error_message = 'No bank account on file'
                payment.save()
                continue
            
            bank_account = payment.employee.bank_account
            
            if bank_account.verification_status != 'verified':
                payment.status = 'failed'
                payment.error_message = 'Bank account not verified'
                payment.save()
                continue
            
            # Create transaction
            txn_ref = f"TXN-{batch.batch_id}-{payment.employee.id}-{uuid.uuid4().hex[:8].upper()}"
            
            bank_txn = BankTransaction.objects.create(
                salary_payment=payment,
                transaction_reference=txn_ref,
                amount=payment.amount,
                status='prepared',
                bank_account_snapshot={
                    'account_holder': bank_account.account_holder_name,
                    'account_number': bank_account.get_masked_account(),
                    'bank_name': bank_account.bank_name,
                    'routing_code': bank_account.routing_code,
                }
            )
            
            transactions.append(bank_txn)
        
        return transactions
    
    @staticmethod
    def generate_bank_file(batch, file_format='CSV'):
        """Generate bank submission file"""
        transactions = BankTransaction.objects.filter(
            salary_payment__batch=batch,
            status='prepared'
        ).select_related('salary_payment__employee')
        
        if file_format == 'CSV':
            return BankService._generate_csv(batch, transactions)
        elif file_format == 'NACHA':
            return BankService._generate_nacha(batch, transactions)
        else:
            raise ValueError(f"Unsupported format: {file_format}")
    
    @staticmethod
    def _generate_csv(batch, transactions):
        """Generate CSV format"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Transaction Reference',
            'Employee ID',
            'Account Holder Name',
            'Account Number',
            'Bank Name',
            'Routing Code',
            'Amount',
            'Currency',
            'Payment Date',
            'Remarks'
        ])
        
        # Data rows
        for txn in transactions:
            payment = txn.salary_payment
            employee = payment.employee
            bank_account = employee.bank_account
            
            writer.writerow([
                txn.transaction_reference,
                employee.employee_id,
                bank_account.account_holder_name,
                bank_account.get_account_number(),  # Full number for bank
                bank_account.bank_name,
                bank_account.routing_code,
                float(txn.amount),
                txn.currency,
                payment.payment_date.strftime('%Y-%m-%d') if payment.payment_date else '',
                f"Salary for {payment.month}/{payment.year}"
            ])
        
        content = output.getvalue()
        output.close()
        
        # Calculate hash
        file_hash = hashlib.sha256(content.encode()).hexdigest()
        
        # Store submission file
        file_name = f"payroll_{batch.batch_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        submission_file = BankSubmissionFile.objects.create(
            batch=batch,
            file_name=file_name,
            file_format='CSV',
            file_content=content,
            file_hash=file_hash,
            submitted_by=batch.processed_by
        )
        
        return {
            'file_name': file_name,
            'content': content,
            'hash': file_hash,
            'submission_file': submission_file
        }
    
    @staticmethod
    def _generate_nacha(batch, transactions):
        """Generate NACHA format (ACH file for US banks)"""
        # Placeholder - implement NACHA format
        lines = []
        
        # File Header Record (Type 1)
        lines.append("1" + "0" * 93)  # Simplified
        
        # Batch Header Record (Type 5)
        lines.append("5" + "0" * 93)
        
        # Entry Detail Records (Type 6)
        for txn in transactions:
            # Simplified entry
            lines.append("6" + "0" * 93)
        
        # Batch Control Record (Type 8)
        lines.append("8" + "0" * 93)
        
        # File Control Record (Type 9)
        lines.append("9" + "0" * 93)
        
        content = "\n".join(lines)
        file_hash = hashlib.sha256(content.encode()).hexdigest()
        
        file_name = f"payroll_{batch.batch_id}.ach"
        
        submission_file = BankSubmissionFile.objects.create(
            batch=batch,
            file_name=file_name,
            file_format='NACHA',
            file_content=content,
            file_hash=file_hash,
            submitted_by=batch.processed_by
        )
        
        return {
            'file_name': file_name,
            'content': content,
            'hash': file_hash,
            'submission_file': submission_file
        }
    
    @staticmethod
    @transaction.atomic
    def submit_to_bank(batch, user):
        """Submit batch to bank"""
        # Generate file
        result = BankService.generate_bank_file(batch, 'CSV')
        
        # Update transaction statuses
        BankTransaction.objects.filter(
            salary_payment__batch=batch,
            status='prepared'
        ).update(
            status='submitted',
            submitted_at=timezone.now()
        )
        
        # Update batch
        batch.status = 'processing'
        batch.save()
        
        # In production: Actually submit to bank API
        # bank_api.submit_file(result['content'])
        
        return result
    
    @staticmethod
    def process_bank_response(transaction_reference, bank_reference, status, response_data):
        """Process bank response"""
        try:
            txn = BankTransaction.objects.get(transaction_reference=transaction_reference)
            txn.bank_reference = bank_reference
            txn.status = status
            txn.bank_response = response_data
            
            if status == 'settled':
                txn.settled_at = timezone.now()
                txn.salary_payment.status = 'paid'
                txn.salary_payment.payment_date = timezone.now()
                txn.salary_payment.save()
            elif status == 'failed' or status == 'returned':
                txn.salary_payment.status = 'failed'
                txn.salary_payment.error_message = response_data.get('error', 'Payment failed')
                txn.salary_payment.save()
            
            txn.save()
            return txn
        except BankTransaction.DoesNotExist:
            return None
    
    @staticmethod
    def reconcile_transactions(bank_statement_data, reconciliation_date=None):
        """Reconcile transactions with bank statement"""
        if not reconciliation_date:
            reconciliation_date = date.today()
        
        results = {
            'matched': [],
            'missing_in_bank': [],
            'missing_in_system': [],
            'amount_mismatch': [],
        }
        
        # Get unreconciled transactions
        system_txns = BankTransaction.objects.filter(
            reconciled=False,
            status__in=['submitted', 'processing', 'settled']
        )
        
        system_refs = {txn.transaction_reference: txn for txn in system_txns}
        bank_refs = {entry['reference']: entry for entry in bank_statement_data}
        
        # Match transactions
        for ref, txn in system_refs.items():
            if ref in bank_refs:
                bank_entry = bank_refs[ref]
                
                # Check amount
                if Decimal(str(bank_entry['amount'])) == txn.amount:
                    # Match!
                    txn.reconciled = True
                    txn.reconciled_at = timezone.now()
                    txn.bank_reference = bank_entry.get('bank_ref', '')
                    txn.save()
                    results['matched'].append(txn)
                else:
                    # Amount mismatch
                    results['amount_mismatch'].append(txn)
                    ReconciliationException.objects.create(
                        transaction=txn,
                        exception_type='amount_mismatch',
                        expected_amount=txn.amount,
                        actual_amount=Decimal(str(bank_entry['amount'])),
                        description=f"Amount mismatch for {ref}"
                    )
            else:
                # Missing in bank
                results['missing_in_bank'].append(txn)
                ReconciliationException.objects.create(
                    transaction=txn,
                    exception_type='missing_bank',
                    description=f"Transaction {ref} not found in bank statement"
                )
        
        # Check for entries in bank but not in system
        for ref, entry in bank_refs.items():
            if ref not in system_refs:
                results['missing_in_system'].append(entry)
                ReconciliationException.objects.create(
                    exception_type='missing_system',
                    description=f"Bank entry {ref} not found in system",
                    actual_amount=Decimal(str(entry['amount']))
                )
        
        return results
    
    @staticmethod
    def retry_failed_transaction(transaction_id, user):
        """Retry a failed transaction"""
        try:
            with transaction.atomic():
                txn = BankTransaction.objects.select_for_update().get(pk=transaction_id)
                
                if txn.status not in ['failed', 'returned']:
                    return {'success': False, 'message': 'Transaction not in failed state'}
                
                # Reset status
                txn.status = 'prepared'
                txn.error_message = ''
                txn.save()
                
                # Reset payment
                txn.salary_payment.status = 'approved'
                txn.salary_payment.error_message = ''
                txn.salary_payment.save()
                
                return {'success': True, 'transaction': txn}
        except Exception as e:
            return {'success': False, 'message': str(e)}
