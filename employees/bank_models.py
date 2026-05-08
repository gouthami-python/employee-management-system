"""
Bank Account and Transaction Models for Payroll
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Employee
from cryptography.fernet import Fernet
from django.conf import settings


class BankAccount(models.Model):
    """Employee bank account details with verification"""
    
    ACCOUNT_TYPES = [
        ('savings', 'Savings'),
        ('checking', 'Checking'),
        ('current', 'Current'),
    ]
    
    VERIFICATION_STATUS = [
        ('unverified', 'Unverified'),
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('failed', 'Verification Failed'),
    ]
    
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='bank_account')
    
    # Bank details (encrypted)
    account_holder_name = models.CharField(max_length=200)
    account_number_encrypted = models.BinaryField()  # Encrypted
    bank_name = models.CharField(max_length=200)
    branch_name = models.CharField(max_length=200, blank=True)
    routing_code = models.CharField(max_length=50)  # IFSC/SWIFT/Routing
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='savings')
    
    # Verification
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='unverified')
    verification_date = models.DateTimeField(null=True, blank=True)
    verification_method = models.CharField(max_length=50, blank=True)  # micro_deposit, api, manual
    verification_proof = models.TextField(blank=True)  # JSON with verification details
    
    # Consent
    consent_given = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True)
    consent_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Audit
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='bank_accounts_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bank_accounts_updated')
    updated_at = models.DateTimeField(auto_now=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.employee} - {self.bank_name} ({self.verification_status})"
    
    def set_account_number(self, account_number):
        """Encrypt and store account number"""
        cipher = Fernet(settings.ENCRYPTION_KEY.encode())
        self.account_number_encrypted = cipher.encrypt(account_number.encode())
    
    def get_account_number(self):
        """Decrypt and return account number"""
        cipher = Fernet(settings.ENCRYPTION_KEY.encode())
        return cipher.decrypt(self.account_number_encrypted).decode()
    
    def get_masked_account(self):
        """Return masked account number (last 4 digits)"""
        try:
            full = self.get_account_number()
            return f"****{full[-4:]}"
        except:
            return "****"


class BankTransaction(models.Model):
    """Track individual bank transactions"""
    
    STATUS_CHOICES = [
        ('prepared', 'Prepared'),
        ('submitted', 'Submitted to Bank'),
        ('accepted', 'Accepted by Bank'),
        ('processing', 'Processing'),
        ('settled', 'Settled'),
        ('returned', 'Returned'),
        ('failed', 'Failed'),
    ]
    
    # Link to payment
    salary_payment = models.OneToOneField('SalaryPayment', on_delete=models.CASCADE, related_name='bank_transaction')
    
    # Transaction details
    transaction_reference = models.CharField(max_length=100, unique=True, db_index=True)
    bank_reference = models.CharField(max_length=100, blank=True, db_index=True)  # From bank
    utr_number = models.CharField(max_length=50, blank=True)  # Unique Transaction Reference
    
    # Amount
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='prepared')
    
    # Bank details snapshot (at time of transaction)
    bank_account_snapshot = models.JSONField()  # Store bank details used
    
    # Timestamps
    prepared_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    settled_at = models.DateTimeField(null=True, blank=True)
    
    # Bank responses
    bank_response = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Reconciliation
    reconciled = models.BooleanField(default=False)
    reconciled_at = models.DateTimeField(null=True, blank=True)
    reconciled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reconciled_transactions')
    
    class Meta:
        ordering = ['-prepared_at']
        indexes = [
            models.Index(fields=['status', 'reconciled']),
            models.Index(fields=['bank_reference']),
        ]
    
    def __str__(self):
        return f"{self.transaction_reference} - {self.status}"


class BankSubmissionFile(models.Model):
    """Store bank submission files for audit"""
    
    batch = models.ForeignKey('PayrollBatch', on_delete=models.CASCADE, related_name='submission_files')
    
    file_name = models.CharField(max_length=255)
    file_format = models.CharField(max_length=50)  # NACHA, SEPA, CSV, etc.
    file_content = models.TextField()  # Actual file content
    file_hash = models.CharField(max_length=64)  # SHA256 hash
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Bank confirmation
    bank_confirmation = models.TextField(blank=True)
    bank_file_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.file_name} - {self.batch.batch_id}"


class ReconciliationException(models.Model):
    """Track reconciliation exceptions"""
    
    EXCEPTION_TYPES = [
        ('missing_bank', 'Missing in Bank Statement'),
        ('missing_system', 'Missing in System'),
        ('amount_mismatch', 'Amount Mismatch'),
        ('duplicate', 'Duplicate Entry'),
        ('returned', 'Payment Returned'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    transaction = models.ForeignKey(BankTransaction, on_delete=models.CASCADE, related_name='exceptions', null=True, blank=True)
    
    exception_type = models.CharField(max_length=20, choices=EXCEPTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Details
    expected_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField()
    
    # Assignment
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_exceptions')
    
    # Resolution
    resolution_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_exceptions')
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.exception_type} - {self.status}"
