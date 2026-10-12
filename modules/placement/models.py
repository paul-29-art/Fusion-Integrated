from django.db import models
from django.contrib.auth.models import User, Group

class LeaveCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    days = models.FloatField()
    supports_half_days = models.BooleanField(default=False)
    continuous_count = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Station(models.Model):
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('AWAITING_SUBSTITUTE', 'Awaiting Substitute'),
        ('AWAITING_UNIT_HEAD_REVIEW', 'Awaiting Unit Head
Review'),
        ('AWAITING_ESTABLISHMENT_ROUTING', 'Awaiting
Establishment Routing'),
        ('AWAITING_FINAL_SANCTION', 'Awaiting Final Sanction'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('WITHDRAWN', 'Withdrawn'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(LeaveCategory,
on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    station = models.ForeignKey(Station, on_delete=models.CASCADE,
null=True, blank=True)
    substitute = models.ForeignKey(User, on_delete=models.CASCADE,
related_name='substitute_for', null=True, blank=True)
    status = models.CharField(max_length=255,
choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} - {self.category.name} -
{self.start_date} to {self.end_date}'

    def clean(self):
        if self.start_date > self.end_date:
            raise models.ValidationError("End date must be later
than start date.")
        if self.status == 'APPROVED' and not self.substitute:
            raise models.ValidationError("An approved leave
request must have a substitute.")

class LeaveBalance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(LeaveCategory,
on_delete=models.CASCADE)
    balance = models.FloatField(default=0)

    def __str__(self):
        return f'{self.user.username} - {self.category.name}
Balance: {self.balance}'

    def save(self, *args, **kwargs):
        if self.category.continuous_count:
            holidays =
Holiday.objects.filter(date__range=[self.user.date_joined,
self.user.last_login])
            days_count = (self.user.last_login -
self.user.date_joined).days
            if holidays:
                days_count -= holidays.count()
            self.balance += self.category.days * days_count
        super().save(*args, **kwargs)

class Holiday(models.Model):
    date = models.DateField(unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.date} - {self.name}