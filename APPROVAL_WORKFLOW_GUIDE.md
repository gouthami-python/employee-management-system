# 🔐 Approval Workflow - User Guide

## ✅ What's New

Your salary management now has a **3-step approval workflow**:

```
1. PREPARE → 2. APPROVE → 3. EXECUTE
```

---

## 🎯 How It Works

### **Step 1: PREPARE Payroll** (Preparer Role)

1. Go to `/admin-panel/salary/`
2. Click **"Pay Salary"** tab
3. Select month/year
4. Select employees
5. **Choose approval mode:**
   - ✅ **Check "Auto-approve"** → Pays immediately (if < $10,000)
   - ⬜ **Uncheck "Auto-approve"** → Requires approval (if >= $10,000)
6. Click **"Process Payroll"**

**Result:**
- If auto-approve + amount < $10,000: ✅ **Paid immediately**
- If amount >= $10,000: ⏳ **Batch created, pending approval**

---

### **Step 2: APPROVE Batch** (Approver Role)

1. Go to `/admin-panel/salary/`
2. Click **"Pending Approval"** tab
3. See list of batches waiting for approval
4. Click **"Approve"** button
5. Add remarks (optional)
6. Confirm approval

**Result:**
- Batch status: `pending_approval` → `approved`
- Batch moves to "Ready to Execute" section

---

### **Step 3: EXECUTE Payment** (Executor Role)

1. In **"Pending Approval"** tab
2. Scroll to **"Approved Batches (Ready to Execute)"**
3. Click **"Execute Payment"** button
4. Confirm execution

**Result:**
- Payments processed
- Status: `approved` → `paid`
- Employees receive salary

---

## 💰 Approval Threshold

**Default: $10,000**

- **Total < $10,000** → Can auto-approve
- **Total >= $10,000** → Requires approval

**Example:**
- 5 employees × $1,500 = $7,500 → ✅ Can auto-approve
- 10 employees × $2,000 = $20,000 → ⏳ Requires approval

---

## 📊 Workflow Diagram

```
┌─────────────────────────────────────────────────────────┐
│ ADMIN PREPARES PAYROLL                                  │
│ - Selects employees                                     │
│ - Chooses auto-approve or manual                        │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ├─── Auto-approve? ───┐
                  │                     │
                  NO                   YES
                  │                     │
                  ▼                     ▼
    ┌─────────────────────┐   ┌──────────────────┐
    │ PENDING APPROVAL    │   │ PAID IMMEDIATELY │
    │ Status: pending     │   │ Status: paid     │
    └──────────┬──────────┘   └──────────────────┘
               │
               ▼
    ┌─────────────────────┐
    │ APPROVER REVIEWS    │
    │ - Checks details    │
    │ - Approves/Rejects  │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ APPROVED            │
    │ Status: approved    │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ EXECUTOR PROCESSES  │
    │ - Executes payment  │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │ PAID                │
    │ Status: paid        │
    └─────────────────────┘
```

---

## 🎭 User Roles

### **Preparer**
- Can create payroll batches
- Can select employees
- Can choose auto-approve

### **Approver**
- Can approve/reject batches
- Can add approval remarks
- Reviews batch details

### **Executor**
- Can execute approved batches
- Processes actual payments
- Marks as paid

**Note:** Currently all admins have all roles. In production, assign specific roles.

---

## 📋 UI Changes

### **New Tab: "Pending Approval"**

Shows two sections:

1. **Batches Pending Approval**
   - Batch ID
   - Month/Year
   - Employee count
   - Total amount
   - Created by
   - Actions: Approve / Reject

2. **Approved Batches (Ready to Execute)**
   - Batch ID
   - Total amount
   - Approved by
   - Approved date
   - Action: Execute Payment

### **Updated "Pay Salary" Tab**

New checkbox:
```
☐ Auto-approve and pay immediately (skip approval if < $10,000)
```

- **Checked** → Pays immediately (if under threshold)
- **Unchecked** → Always requires approval

---

## 🔍 Audit Trail

Every batch tracks:

| Field | Description |
|-------|-------------|
| `created_by` | Who prepared the batch |
| `created_at` | When prepared |
| `approved_by` | Who approved |
| `approved_at` | When approved |
| `processed_by` | Who executed |
| `processed_at` | When executed |
| `remarks` | Approval notes |

**View audit trail:**
- Go to `/admin-panel/payroll/reports/`
- See "Recent Payroll Batches" section

---

## 💡 Usage Examples

### **Example 1: Small Payroll (Auto-Approve)**

```
Scenario: Pay 5 employees, total $7,500

Steps:
1. Select 5 employees
2. ✅ Check "Auto-approve"
3. Click "Process Payroll"

Result: ✅ Paid immediately
Message: "✓ Paid 5 employees for 12/2024"
```

### **Example 2: Large Payroll (Requires Approval)**

```
Scenario: Pay 20 employees, total $35,000

Steps:
1. Select 20 employees
2. ⬜ Uncheck "Auto-approve" (or leave unchecked)
3. Click "Process Payroll"

Result: ⏳ Batch created, pending approval
Message: "Batch BATCH-202412-ABC123 created and pending approval. Total: $35,000"

Then:
4. Go to "Pending Approval" tab
5. Click "Approve"
6. Add remarks: "December payroll approved"
7. Click "Approve Batch"

Result: ✅ Batch approved
Message: "Batch BATCH-202412-ABC123 approved successfully!"

Finally:
8. In "Approved Batches" section
9. Click "Execute Payment"
10. Confirm

Result: ✅ Payments processed
Message: "Batch executed! 20 payments processed."
```

### **Example 3: Reject Batch**

```
Scenario: Found error in batch

Steps:
1. Go to "Pending Approval" tab
2. Click "Reject" button
3. Enter reason: "Incorrect salary for John Doe"
4. Click "Reject Batch"

Result: ❌ Batch rejected
Status: cancelled
```

---

## 🔧 Configuration

### **Change Approval Threshold**

Edit `views.py`:
```python
# Line ~50
approval_threshold=10000  # Change to desired amount
```

**Examples:**
- `5000` → Approve if >= $5,000
- `50000` → Approve if >= $50,000
- `0` → Always require approval

### **Disable Approval Workflow**

Set threshold very high:
```python
approval_threshold=999999999  # Effectively disables
```

Or always use auto-approve checkbox.

---

## 📊 Status Flow

```
Payment Status Progression:

draft → pending_approval → approved → processing → paid
                                              ↓
                                          failed
```

**Status Meanings:**
- `draft` - Being prepared
- `pending_approval` - Waiting for approval
- `approved` - Approved, ready to execute
- `processing` - Being executed
- `paid` - Successfully paid
- `failed` - Payment failed
- `cancelled` - Batch rejected

---

## ✅ Benefits

### **1. Separation of Duties**
- Preparer ≠ Approver ≠ Executor
- Reduces fraud risk
- Compliance requirement

### **2. Review Before Payment**
- Catch errors before money moves
- Verify amounts
- Check employee list

### **3. Audit Trail**
- Complete history
- Who did what, when
- Compliance ready

### **4. Flexibility**
- Small amounts: auto-approve
- Large amounts: require approval
- Configurable threshold

---

## 🚨 Troubleshooting

### **Issue: Can't find "Pending Approval" tab**
**Solution:** Refresh page, it's the 3rd tab

### **Issue: Batch not showing in pending**
**Solution:** Check if auto-approve was enabled and amount < threshold

### **Issue: Can't execute approved batch**
**Solution:** Make sure batch status is "approved", not "pending_approval"

### **Issue: Want to cancel pending batch**
**Solution:** Click "Reject" and enter reason

---

## 📈 Reporting

View approval workflow in reports:

1. Go to `/admin-panel/payroll/reports/`
2. See "Recent Payroll Batches" table
3. Shows:
   - Batch ID
   - Status
   - Created by
   - Approved by
   - Processed by
   - Timestamps

---

## 🎯 Best Practices

1. **Always review before approving**
   - Check employee list
   - Verify amounts
   - Confirm month/year

2. **Add meaningful remarks**
   - "December 2024 payroll"
   - "Bonus included for top performers"
   - "Adjusted for new hires"

3. **Execute promptly after approval**
   - Don't leave approved batches pending
   - Process same day if possible

4. **Monitor pending queue**
   - Check daily
   - Don't let batches pile up

5. **Use auto-approve wisely**
   - For regular small payrolls
   - When confident in data
   - Not for first-time runs

---

## 🔐 Security Notes

- All actions logged with user, IP, timestamp
- Approval cannot be bypassed (except auto-approve)
- Batch cannot be modified after creation
- Complete audit trail maintained

---

## ✅ Summary

**What Changed:**
- ✅ Added approval workflow
- ✅ New "Pending Approval" tab
- ✅ Auto-approve checkbox
- ✅ Approve/Reject buttons
- ✅ Execute payment button
- ✅ Complete audit trail

**What Stayed Same:**
- ✅ All existing features work
- ✅ Salary updates
- ✅ Bonus system
- ✅ Payment history
- ✅ Reports

**Status: FULLY OPERATIONAL** 🚀

---

**Need help? Check the main documentation or contact support.**
