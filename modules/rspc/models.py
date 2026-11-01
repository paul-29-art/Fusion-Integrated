from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ResearchProposal(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted to HoD'),
        ('HOD_APPROVED', 'Approved by HoD'),
        ('DEAN_APPROVED', 'Approved by Dean RSPC'),
        ('REJECTED', 'Rejected'),
    ]

    title = models.CharField(max_length=255)
    pi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proposals')
    co_pi = models.CharField(max_length=255, blank=True)
    sponsor_agency = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    duration_months = models.PositiveIntegerField(default=12)
    abstract = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.status})"


class ConsultancyProject(models.Model):
    STATUS_CHOICES = [
        ('PROPOSED', 'Proposed'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
    ]

    title = models.CharField(max_length=255)
    pi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consultancies')
    client_name = models.CharField(max_length=255)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    institutional_share = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    investigator_share = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    duration_months = models.PositiveIntegerField(default=6)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PROPOSED')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.total_cost:
            cost = Decimal(str(self.total_cost))
            self.institutional_share = (cost * Decimal('0.30')).quantize(Decimal('0.01'))
            self.investigator_share = (cost * Decimal('0.70')).quantize(Decimal('0.01'))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.client_name}"


class FinancialRequest(models.Model):
    TYPE_CHOICES = [
        ('DISBURSEMENT', 'Fund Disbursement'),
        ('PROCUREMENT', 'Equipment Procurement'),
        ('TRAVEL', 'Travel Allowance'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    proposal = models.ForeignKey(ResearchProposal, on_delete=models.CASCADE, related_name='financial_requests')
    request_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='DISBURSEMENT')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    justification = models.TextField()
    requires_director_approval = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.amount and Decimal(str(self.amount)) > Decimal('500000'):
            self.requires_director_approval = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.request_type} - ₹{self.amount} ({self.status})"


class ProjectReport(models.Model):
    REPORT_TYPES = [
        ('ANNUAL', 'Annual Progress Report'),
        ('FINAL', 'Final Project Completion Report'),
    ]
    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('ACCEPTED', 'Accepted'),
    ]

    proposal = models.ForeignKey(ResearchProposal, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, default='ANNUAL')
    summary = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUBMITTED')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.report_type} for {self.proposal.title}"
