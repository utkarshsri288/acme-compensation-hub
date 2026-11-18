from decimal import Decimal
from django.db import models

class Employee(models.Model):
    STATUS_CHOICES = [("active", "Active"), ("on_leave", "On leave"), ("inactive", "Inactive")]
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField(unique=True)
    country = models.CharField(max_length=80, db_index=True)
    department = models.CharField(max_length=80, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active", db_index=True)
    start_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def full_name(self): return f"{self.first_name} {self.last_name}"

class SalaryRecord(models.Model):
    FREQUENCY_CHOICES = [("annual", "Annual"), ("monthly", "Monthly"), ("biweekly", "Biweekly"), ("weekly", "Weekly")]
    CURRENCIES = [(c, c) for c in ("USD", "INR", "GBP", "EUR", "SGD", "AUD")]
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name="salary")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCIES)
    pay_frequency = models.CharField(max_length=12, choices=FREQUENCY_CHOICES, default="annual")
    effective_date = models.DateField()
    updated_at = models.DateTimeField(auto_now=True)
    def annualized(self):
        return self.amount * {"annual": 1, "monthly": 12, "biweekly": 26, "weekly": 52}[self.pay_frequency]

class SalaryHistory(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="salary_history")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3)
    pay_frequency = models.CharField(max_length=12)
    effective_date = models.DateField()
    reason = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class AuditEvent(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="audit_events")
    action = models.CharField(max_length=80)
    changed_fields = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
