from datetime import date
from decimal import Decimal
from io import StringIO
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from .models import Employee, SalaryRecord, AuditEvent, SalaryHistory
from .roles import ADMIN, HR_MANAGER

class CompensationApiTests(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(first_name="Priya", last_name="Patel", email="priya@example.com", country="India", department="Engineering", status="active", start_date=date(2024, 1, 15))
        SalaryRecord.objects.create(employee=self.employee, amount=Decimal("100000"), currency="USD", pay_frequency="annual", effective_date=date(2024, 1, 15))
        self.user = get_user_model().objects.create_user(username="test_hr", password="password", email="test@example.com", first_name="Test", last_name="HR")
        self.user.groups.add(Group.objects.get(name=HR_MANAGER))
        self.client = APIClient(); self.client.force_authenticate(user=self.user)
    def test_login_returns_token(self):
        self.client.logout(); response = self.client.post("/api/auth/login", {"username": "test_hr", "password": "password"}, format="json")
        self.assertEqual(response.status_code, 200); self.assertTrue(response.json()["token"])
        self.assertEqual(response.json()["user"]["role"], HR_MANAGER)
        self.assertEqual(self.client.post("/api/auth/login", {"username": "test@example.com", "password": "password"}, format="json").status_code, 401)
        self.assertEqual(self.client.post("/api/auth/login", {"username": [], "password": {}}, format="json").status_code, 400)
    def test_health_and_directory(self):
        self.assertEqual(self.client.get("/api/health").status_code, 200)
        response = self.client.get("/api/employees?search=Priya")
        self.assertEqual(response.status_code, 200); self.assertEqual(response.json()["meta"]["total"], 1)
        self.assertNotIn("salary_history", response.json()["data"][0])
        self.assertEqual(self.client.get("/api/employees?status=on_leave").json()["meta"]["total"], 0)
    def test_dashboard_annualizes_monthly_salary(self):
        self.employee.salary.pay_frequency = "monthly"; self.employee.salary.amount = Decimal("10000"); self.employee.salary.save()
        response = self.client.get("/api/dashboard").json()
        self.assertEqual(response["headcount"], 1); self.assertEqual(response["payroll_usd"], 120000.0)
    def test_salary_patch_creates_audit_event(self):
        response = self.client.patch(f"/api/employees/{self.employee.id}", {"amount": "120000", "currency": "USD", "pay_frequency": "annual", "effective_date": "2025-01-01"}, format="json")
        self.assertEqual(response.status_code, 200); self.assertEqual(AuditEvent.objects.count(), 1); self.assertEqual(response.json()["salary"]["amount"], "120000.00")
        history = response.json()["salary_history"]
        self.assertEqual([item["amount"] for item in history], ["100000.00", "120000.00"])
        self.assertEqual([item["reason"] for item in history], ["Original record", "Salary update"])
        self.assertEqual(SalaryHistory.objects.count(), 2)

    def test_salary_sort_uses_annualized_usd_across_currencies(self):
        low = Employee.objects.create(first_name="Alex", last_name="Reed", email="alex@example.com", country="India", department="People", start_date=date(2024, 1, 15))
        SalaryRecord.objects.create(employee=low, amount=Decimal("500000"), currency="INR", pay_frequency="annual", effective_date=date(2024, 1, 15))
        high = Employee.objects.create(first_name="Sam", last_name="Lee", email="sam@example.com", country="United States", department="People", start_date=date(2024, 1, 15))
        SalaryRecord.objects.create(employee=high, amount=Decimal("10000"), currency="USD", pay_frequency="monthly", effective_date=date(2024, 1, 15))
        ascending = self.client.get("/api/employees?sort=salary&direction=asc").json()["data"]
        descending = self.client.get("/api/employees?sort=salary&direction=desc").json()["data"]
        self.assertEqual([row["id"] for row in ascending], [low.id, self.employee.id, high.id])
        self.assertEqual([row["id"] for row in descending], [high.id, self.employee.id, low.id])

    def test_invalid_pagination_returns_validation_error(self):
        response = self.client.get("/api/employees?page=abc")
        self.assertEqual(response.status_code, 400)
    def test_salary_noop_does_not_create_history(self):
        response = self.client.patch(f"/api/employees/{self.employee.id}", {"amount": "100000.00"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(SalaryHistory.objects.count(), 0)
        self.assertEqual(AuditEvent.objects.count(), 0)
    def test_export_matches_filtered_page_and_requires_login(self):
        other = Employee.objects.create(first_name="Alex", last_name="Reed", email="alex@example.com", country="Germany", department="People", start_date=date(2024, 1, 15))
        SalaryRecord.objects.create(employee=other, amount=Decimal("90000"), currency="EUR", pay_frequency="annual", effective_date=date(2024, 1, 15))
        response = self.client.get("/api/employees/export?country=India&status=active&page_size=12")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Priya Patel", response.content.decode())
        self.assertNotIn("Alex Reed", response.content.decode())
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get("/api/employees/export").status_code, 401)

class AdminAccessTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(username="admin_user", password="AdminPass123!", is_staff=True, is_superuser=True)
        self.hr = User.objects.create_user(username="hr_user", password="HrPass123!")
        self.admin.groups.add(Group.objects.get(name=ADMIN))
        self.hr.groups.add(Group.objects.get(name=HR_MANAGER))
        self.client = APIClient()

    def test_only_admin_can_create_users_and_transfer_role(self):
        self.client.force_authenticate(user=self.hr)
        self.assertEqual(self.client.get("/api/admin/users").status_code, 403)
        self.assertEqual(self.client.post("/api/admin/users", {"username": "new_hr", "name": "A", "email": "new@example.com", "password": "Password123!"}, format="json").status_code, 403)
        self.client.force_authenticate(user=self.admin)
        self.assertEqual(self.client.patch(f"/api/admin/users/{self.admin.id}", {"is_active": False}, format="json").status_code, 400)
        self.assertEqual(self.client.post("/api/admin/users", {"username": "new_hr", "name": "A", "email": "bad-email", "password": "Password123!"}, format="json").status_code, 400)
        created = self.client.post("/api/admin/users", {"username": "new_hr", "name": "New HR", "email": "new@example.com", "password": "Password123!"}, format="json")
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.json()["role"], HR_MANAGER)
        self.assertEqual(created.json()["username"], "new_hr")
        self.assertEqual(self.client.post("/api/admin/users", {"username": "new_hr", "name": "Other HR", "email": "other@example.com", "password": "Password123!"}, format="json").status_code, 400)
        response = self.client.patch(f"/api/admin/users/{self.hr.id}", {"transfer_admin": True}, format="json")
        self.assertEqual(response.status_code, 200)
        self.admin.refresh_from_db(); self.hr.refresh_from_db()
        self.assertFalse(self.admin.is_staff)
        self.assertTrue(self.hr.is_staff)
        self.assertTrue(self.admin.groups.filter(name=HR_MANAGER).exists())
        self.assertTrue(self.hr.groups.filter(name=ADMIN).exists())
        self.client.force_authenticate(user=self.admin)
        self.assertEqual(self.client.get("/api/admin/users").status_code, 403)

    def test_create_user_rejects_weak_passwords(self):
        self.client.force_authenticate(user=self.admin)
        weak_passwords = (
            "Ab1!",
            "lowercase1!",
            "UPPERCASE1!",
            "NoNumbers!",
            "NoSymbols123",
            "New_hr123!",
        )
        for password in weak_passwords:
            with self.subTest(password=password):
                response = self.client.post("/api/admin/users", {
                    "username": "new_hr", "name": "New HR", "email": "new@example.com", "password": password,
                }, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn("Password needs", response.json()["detail"])
        self.assertFalse(get_user_model().objects.filter(username="new_hr").exists())

    def test_inactive_user_cannot_receive_admin_role(self):
        self.hr.is_active = False
        self.hr.save(update_fields=["is_active"])
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(f"/api/admin/users/{self.hr.id}", {"transfer_admin": True}, format="json")
        self.assertEqual(response.status_code, 400)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_staff)
        self.assertEqual(self.client.patch(f"/api/admin/users/{self.hr.id}", {"is_active": "false"}, format="json").status_code, 400)

    def test_user_without_workspace_role_cannot_view_salary_data(self):
        outsider = get_user_model().objects.create_user(username="outsider", password="Password123!")
        self.client.force_authenticate(user=outsider)
        self.assertEqual(self.client.get("/api/employees").status_code, 403)
        self.assertEqual(self.client.get("/api/dashboard").status_code, 403)

    def test_demo_seed_does_not_restore_transferred_admin(self):
        self.admin.email = "hr.manager@acme.example"
        self.admin.save(update_fields=["email"])
        self.admin.is_staff = False
        self.admin.is_superuser = False
        self.admin.save(update_fields=["is_staff", "is_superuser"])
        self.admin.groups.set([Group.objects.get(name=HR_MANAGER)])
        call_command("seed_hr_user", stdout=StringIO())
        self.admin.refresh_from_db()
        self.assertFalse(self.admin.is_staff)
        self.assertTrue(self.admin.groups.filter(name=HR_MANAGER).exists())
        self.assertTrue(self.admin.check_password("AdminPass123!"))

    def test_demo_seed_creates_username_and_admin_role(self):
        with override_settings(DEBUG=True):
            call_command("seed_hr_user", stdout=StringIO())
        seeded = get_user_model().objects.get(username="acme_admin")
        self.assertEqual(seeded.email, "hr.manager@acme.example")
        self.assertTrue(seeded.groups.filter(name=ADMIN).exists())
        self.assertTrue(seeded.check_password("AcmeHR2026!"))

    def test_production_seed_prompts_for_unique_password_without_echoing(self):
        with override_settings(DEBUG=False), patch(
            "compensation.management.commands.seed_hr_user.getpass",
            side_effect=["StrongAppPass123!", "StrongAppPass123!"],
        ):
            call_command("seed_hr_user", stdout=StringIO())
        seeded = get_user_model().objects.get(username="acme_admin")
        self.assertTrue(seeded.check_password("StrongAppPass123!"))

    def test_employee_seed_is_repeatable_and_rejects_partial_database(self):
        call_command("seed_employees", count=3, stdout=StringIO())
        self.assertEqual(Employee.objects.count(), 3)
        self.assertEqual(SalaryRecord.objects.count(), 3)
        call_command("seed_employees", count=3, stdout=StringIO())
        self.assertEqual(Employee.objects.count(), 3)
        with self.assertRaises(CommandError):
            call_command("seed_employees", count=4, stdout=StringIO())
        SalaryRecord.objects.first().delete()
        with self.assertRaises(CommandError):
            call_command("seed_employees", count=3, stdout=StringIO())
