from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('FACULTY', 'Faculty'),
        ('HOD', 'Head of Department'),
        ('RSPC_ADMIN', 'RSPC Admin'),
        ('DEAN_RSPC', 'Dean RSPC'),
        ('DIRECTOR', 'Director'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='rspc_profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='FACULTY')
    department = models.CharField(max_length=100, default='Computer Science & Engineering')
    designation = models.CharField(max_length=100, default='Assistant Professor')

    def __str__(self):
        return f"{self.user.username} ({self.role}) - {self.department}"


class ResearchProposal(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted to HoD'),
        ('HOD_RECOMMENDED', 'HoD Recommended'),
        ('HOD_REJECTED', 'HoD Not Recommended'),
        ('ADMIN_VERIFIED', 'Admin Verified'),
        ('ADMIN_REJECTED', 'Admin Ineligible for Forwarding'),
        ('DEAN_APPROVED', 'Approved by Dean RSPC'),
        ('DEAN_REJECTED', 'Dean Not Approved'),
        ('FORWARDED_TO_DIRECTOR', 'Forwarded to Director'),
        ('DIRECTOR_APPROVED', 'Approved by Director'),
        ('DIRECTOR_REJECTED', 'Director Not Approved'),
    ]

    title = models.CharField(max_length=255)
    pi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='research_proposals')
    co_pi = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=100, default='CSE')
    sponsor_agency = models.CharField(max_length=255)
    project_type = models.CharField(max_length=50, default='SPONSORED_RESEARCH')
    budget = models.DecimalField(max_digits=14, decimal_places=2)
    duration_months = models.PositiveIntegerField(default=24)
    objectives = models.TextField()
    timeline_details = models.TextField(blank=True)
    resource_requirements = models.TextField(blank=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='DRAFT')
    is_sanctioned = models.BooleanField(default=False)
    sanctioned_budget = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    expenditure_total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    submission_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.pi.username} ({self.status})"


class ConsultancyProject(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Consultancy Submitted'),
        ('HOD_RECOMMENDED', 'Department Recommended'),
        ('HOD_REJECTED', 'Department Not Recommended'),
        ('ADMIN_VERIFIED', 'Admin Verified'),
        ('ADMIN_REJECTED', 'Not Eligible for Forwarding'),
        ('DEAN_APPROVED', 'Approved by Dean'),
        ('DEAN_REJECTED', 'Dean Not Approved'),
        ('FORWARDED_TO_DIRECTOR', 'Forwarded to Director'),
        ('DIRECTOR_APPROVED', 'Approved by Director'),
        ('ACTIVE', 'Active Project'),
        ('COMPLETED', 'Completed'),
    ]

    title = models.CharField(max_length=255)
    pi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultancy_projects')
    client_name = models.CharField(max_length=255)
    client_type = models.CharField(max_length=100, default='Industry')
    scope_of_work = models.TextField()
    deliverables = models.TextField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    total_cost = models.DecimalField(max_digits=14, decimal_places=2)
    institutional_share = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    investigator_share = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='DRAFT')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.total_cost:
            cost = Decimal(str(self.total_cost))
            self.institutional_share = (cost * Decimal('0.30')).quantize(Decimal('0.01'))
            self.investigator_share = (cost * Decimal('0.70')).quantize(Decimal('0.01'))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.client_name} ({self.status})"


class ConsultancyMilestone(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Deliverable'),
        ('SUBMITTED', 'Deliverable Submitted'),
        ('APPROVED', 'Deliverable Approved'),
        ('SETTLED', 'Payment Settled'),
    ]

    consultancy = models.ForeignKey(ConsultancyProject, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=255)
    deliverable_description = models.TextField()
    due_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING')
    settlement_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.consultancy.title} ({self.status})"


class StaffAppointmentRequest(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Appointment Draft'),
        ('REQUESTED', 'Appointment Requested'),
        ('ADMIN_VERIFIED', 'Admin Verified'),
        ('NOT_ELIGIBLE', 'Not Eligible for Forwarding'),
        ('RECOMMENDATION_RECORDED', 'Selection Recommendation Recorded'),
        ('DEAN_APPROVED', 'Approved by Dean RSPC'),
        ('FORWARDED_TO_DIRECTOR', 'Forwarded to Director'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    proposal = models.ForeignKey(ResearchProposal, on_delete=models.CASCADE, null=True, blank=True, related_name='staff_requests')
    consultancy = models.ForeignKey(ConsultancyProject, on_delete=models.CASCADE, null=True, blank=True, related_name='staff_requests')
    faculty = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff_requests')
    position_title = models.CharField(max_length=100)
    duration_months = models.PositiveIntegerField(default=12)
    stipend_amount = models.DecimalField(max_digits=10, decimal_places=2)
    stipend_structure = models.CharField(max_length=255, default='Institutional Norms + HRA')
    advertisement_details = models.TextField(blank=True)
    application_records = models.TextField(blank=True)
    selected_candidate_name = models.CharField(max_length=255, blank=True)
    selection_committee_remarks = models.TextField(blank=True)
    selection_recommended_by_pi = models.BooleanField(default=False)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='DRAFT')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.position_title} - {self.faculty.username} ({self.status})"


class FinancialRequest(models.Model):
    TYPE_CHOICES = [
        ('DISBURSEMENT', 'Fund Disbursement'),
        ('EXPENDITURE', 'Direct Expenditure'),
        ('TRAVEL', 'Travel Allowance'),
        ('CONTINGENCY', 'Contingency Expenditure'),
    ]
    STATUS_CHOICES = [
        ('DRAFT', 'Financial Request Draft'),
        ('SUBMITTED', 'Submitted for Verification'),
        ('VERIFIED', 'Admin Verified'),
        ('NOT_ELIGIBLE', 'Not Eligible for Forwarding'),
        ('DEAN_APPROVED', 'Approved by Dean RSPC'),
        ('FORWARDED_TO_DIRECTOR', 'Forwarded to Director'),
        ('APPROVED', 'Sanctioned & Approved'),
        ('REJECTED', 'Rejected'),
    ]

    proposal = models.ForeignKey(ResearchProposal, on_delete=models.CASCADE, null=True, blank=True, related_name='financial_requests')
    consultancy = models.ForeignKey(ConsultancyProject, on_delete=models.CASCADE, null=True, blank=True, related_name='financial_requests')
    faculty = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_requests')
    request_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='DISBURSEMENT')
    budget_head = models.CharField(max_length=100, default='Consumables / Travel / Contingency')
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    justification = models.TextField()
    requires_director_approval = models.BooleanField(default=False)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='DRAFT')
    admin_verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.amount and Decimal(str(self.amount)) > Decimal('500000'):
            self.requires_director_approval = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.request_type} - ₹{self.amount} ({self.status})"


class ProcurementRequest(models.Model):
    ITEM_TYPES = [
        ('EQUIPMENT', 'Capital Equipment'),
        ('CONSUMABLES', 'Consumables & Lab Supplies'),
    ]
    STATUS_CHOICES = [
        ('DRAFT', 'Procurement Request Draft'),
        ('SUBMITTED', 'Submitted for Verification'),
        ('VERIFIED', 'Admin Verified'),
        ('NOT_ELIGIBLE', 'Not Eligible for Forwarding'),
        ('DEAN_APPROVED', 'Approved by Dean RSPC'),
        ('FORWARDED_TO_DIRECTOR', 'Forwarded to Director'),
        ('APPROVED', 'Sanctioned & Approved'),
        ('REJECTED', 'Rejected'),
    ]

    proposal = models.ForeignKey(ResearchProposal, on_delete=models.CASCADE, related_name='procurement_requests')
    faculty = models.ForeignKey(User, on_delete=models.CASCADE, related_name='procurement_requests')
    item_type = models.CharField(max_length=30, choices=ITEM_TYPES, default='EQUIPMENT')
    item_name = models.CharField(max_length=255)
    estimated_cost = models.DecimalField(max_digits=14, decimal_places=2)
    specifications = models.TextField()
    sanctioned_budget_balance_checked = models.BooleanField(default=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='DRAFT')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item_name} (₹{self.estimated_cost}) - {self.proposal.title}"


class ProjectReport(models.Model):
    REPORT_TYPES = [
        ('ANNUAL', 'Annual Progress Report'),
        ('UTILIZATION', 'Utilization Certificate (UC)'),
        ('FINAL_COMPLETION', 'Final Project Completion Report'),
    ]
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('ACCEPTED', 'Accepted'),
        ('REVISION_REQUESTED', 'Revision Requested'),
    ]

    proposal = models.ForeignKey(ResearchProposal, on_delete=models.CASCADE, related_name='reports')
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_reports')
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES, default='ANNUAL')
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    work_summary = models.TextField()
    utilization_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    milestone_achievements = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='SUBMITTED')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.report_type} for {self.proposal.title}"


class ProjectClosure(models.Model):
    SETTLEMENT_CHOICES = [
        ('PENDING', 'Pending Settlement'),
        ('VERIFIED', 'Settlement Records Verified'),
        ('CLEARED', 'Financial Accounts Cleared'),
    ]
    STATUS_CHOICES = [
        ('DRAFT', 'Closure Draft'),
        ('SUBMITTED', 'Closure Submitted'),
        ('VERIFIED', 'Closure Verified'),
        ('NOT_ELIGIBLE', 'Not Eligible for Forwarding'),
        ('DEAN_APPROVED', 'Approved by Dean'),
        ('FORWARDED_TO_DIRECTOR', 'Forwarded to Director'),
        ('ARCHIVED', 'Project Completed & Archived'),
        ('REJECTED', 'Closure Rejected'),
    ]

    proposal = models.OneToOneField(ResearchProposal, on_delete=models.CASCADE, related_name='closure_record')
    faculty = models.ForeignKey(User, on_delete=models.CASCADE, related_name='closure_records')
    closure_report_summary = models.TextField()
    financial_settlement_status = models.CharField(max_length=30, choices=SETTLEMENT_CHOICES, default='PENDING')
    asset_declaration_verified = models.BooleanField(default=False)
    unspent_balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    dean_remarks = models.TextField(blank=True)
    director_remarks = models.TextField(blank=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='DRAFT')
    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Closure: {self.proposal.title} ({self.status})"


class ReviewDecision(models.Model):
    entity_type = models.CharField(max_length=30)
    entity_id = models.PositiveIntegerField()
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rspc_decisions')
    reviewer_role = models.CharField(max_length=30)
    decision = models.CharField(max_length=40)
    remarks = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer_role} {self.decision} on {self.entity_type} #{self.entity_id} at {self.timestamp}"


class AuditLog(models.Model):
    action = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=50)
    entity_id = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='rspc_audit_logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.action} on {self.entity_type} #{self.entity_id} by {self.user}"


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rspc_notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    category = models.CharField(max_length=50, default='GENERAL')
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To {self.recipient.username}: {self.title}"
