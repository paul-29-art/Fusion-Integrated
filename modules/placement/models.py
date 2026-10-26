from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class LeaveCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    days = models.FloatField(default=0.0)
    supports_half_days = models.BooleanField(default=False)
    continuous_count = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Leave Category"
        verbose_name_plural = "Leave Categories"

    def __str__(self):
        return self.name


class Station(models.Model):
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Station"
        verbose_name_plural = "Stations"

    def __str__(self):
        return self.name


class Holiday(models.Model):
    date = models.DateField(unique=True)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Holiday"
        verbose_name_plural = "Holidays"
        ordering = ['date']

    def __str__(self):
        return f"{self.date} - {self.name}"


class LeaveBalance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_balances')
    category = models.ForeignKey(LeaveCategory, on_delete=models.CASCADE, related_name='balances')
    balance = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('user', 'category')
        verbose_name = "Leave Balance"
        verbose_name_plural = "Leave Balances"

    def __str__(self):
        return f"{self.user.username} - {self.category.name}: {self.balance}"

    def save(self, *args, **kwargs):
        if self.category and self.category.continuous_count and self.user_id:
            if self.user.date_joined and self.user.last_login:
                holidays = Holiday.objects.filter(
                    date__range=[self.user.date_joined.date(), self.user.last_login.date()]
                )
                days_count = (self.user.last_login - self.user.date_joined).days
                if holidays.exists():
                    days_count -= holidays.count()
                self.balance += self.category.days * days_count
        super().save(*args, **kwargs)


class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('AWAITING_SUBSTITUTE', 'Awaiting Substitute'),
        ('AWAITING_UNIT_HEAD_REVIEW', 'Awaiting Unit Head Review'),
        ('AWAITING_ESTABLISHMENT_ROUTING', 'Awaiting Establishment Routing'),
        ('AWAITING_FINAL_SANCTION', 'Awaiting Final Sanction'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('WITHDRAWN', 'Withdrawn'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    category = models.ForeignKey(LeaveCategory, on_delete=models.CASCADE, related_name='leave_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    station = models.ForeignKey(Station, on_delete=models.SET_NULL, null=True, blank=True, related_name='leave_requests')
    station_leave = models.BooleanField(default=False)
    substitute = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='substitute_for', null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PENDING')
    reason = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Leave Request"
        verbose_name_plural = "Leave Requests"

    def __str__(self):
        return f"{self.user.username} - {self.category.name} - {self.start_date} to {self.end_date}"

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("End date must be later than start date.")
        if self.status == 'APPROVED' and not self.substitute:
            raise ValidationError("An approved leave request must have a substitute.")

    @property
    def duration_in_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0


class Substitute(models.Model):
    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE, related_name='substitute_assignments')
    substitute_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='substitute_duties')
    accepted = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Substitute"
        verbose_name_plural = "Substitutes"

    def __str__(self):
        status_text = "Accepted" if self.accepted else "Pending/Declined"
        return f"Substitute {self.substitute_user.username} for Request #{self.leave_request_id} ({status_text})"


class UnitHeadReview(models.Model):
    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE, related_name='unit_head_reviews')
    reviewed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='unit_head_reviews')
    recommended = models.BooleanField(default=True)
    final_sanction = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Unit Head Review"
        verbose_name_plural = "Unit Head Reviews"

    def __str__(self):
        return f"UnitHeadReview for Request #{self.leave_request_id} by {self.reviewed_by.username}"


class EstablishmentVerification(models.Model):
    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE, related_name='establishment_verifications')
    verified_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='establishment_verifications')
    verified = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Establishment Verification"
        verbose_name_plural = "Establishment Verifications"

    def __str__(self):
        status_text = "Verified" if self.verified else "Pending"
        return f"EstablishmentVerification for Request #{self.leave_request_id} ({status_text})"


class DirectorSanction(models.Model):
    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE, related_name='director_sanctions')
    sanctioned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='director_sanctions')
    sanctioned = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Director Sanction"
        verbose_name_plural = "Director Sanctions"

    def __str__(self):
        status_text = "Sanctioned" if self.sanctioned else "Pending/Declined"
        return f"DirectorSanction for Request #{self.leave_request_id} ({status_text})"