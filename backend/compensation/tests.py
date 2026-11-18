from datetime import date
from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from .models import Employee, SalaryRecord, AuditEvent

class CompensationApiTests(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(first_name="Priya", last_name="Patel", email="priya@example.com", country="India", department="Engineering", status="active", start_date=date(2024, 1, 15))
        SalaryRecord.objects.create(employee=self.employee, amount=Decimal("100000"), currency="USD", pay_frequency="annual", effective_date=date(2024, 1, 15))
        self.client = APIClient()
    def test_health_and_directory(self):
        self.assertEqual(self.client.get("/api/health").status_code, 200)
        response = self.client.get("/api/employees?search=Priya")
        self.assertEqual(response.status_code, 200); self.assertEqual(response.json()["meta"]["total"], 1)
    def test_dashboard_annualizes_monthly_salary(self):
        self.employee.salary.pay_frequency = "monthly"; self.employee.salary.amount = Decimal("10000"); self.employee.salary.save()
        response = self.client.get("/api/dashboard").json()
        self.assertEqual(response["headcount"], 1); self.assertEqual(response["payroll_usd"], 120000.0)
    def test_salary_patch_creates_audit_event(self):
        response = self.client.patch(f"/api/employees/{self.employee.id}", {"amount": "120000", "currency": "USD", "pay_frequency": "annual", "effective_date": "2025-01-01"}, format="json")
        self.assertEqual(response.status_code, 200); self.assertEqual(AuditEvent.objects.count(), 1); self.assertEqual(response.json()["salary"]["amount"], "120000.00")
