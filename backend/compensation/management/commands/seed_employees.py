import random
from datetime import date
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from compensation.models import Employee, SalaryRecord

COUNTRIES = [("United States", "USD"), ("India", "INR"), ("United Kingdom", "GBP"), ("Germany", "EUR"), ("Singapore", "SGD"), ("Australia", "AUD")]
DEPARTMENTS = ["Engineering", "People", "Finance", "Sales", "Marketing", "Operations", "Legal"]
FIRST_NAMES = ["Avery", "Maya", "Noah", "Priya", "Lucas", "Sofia", "Ethan", "Amara", "Liam", "Zoe", "Arjun", "Mila"]
LAST_NAMES = ["Patel", "Nguyen", "Morgan", "Singh", "Garcia", "Chen", "Williams", "Kumar", "Smith", "Brown", "Martin", "Mehta"]

class Command(BaseCommand):
    help = "Seed exactly 10,000 deterministic ACME employees."
    def add_arguments(self, parser): parser.add_argument("--count", type=int, default=10000)
    def handle(self, *args, **options):
        count = options["count"]
        if count < 1:
            raise CommandError("Employee count must be positive.")
        existing = Employee.objects.count()
        if existing == count:
            if SalaryRecord.objects.count() != count:
                raise CommandError("Employee count matches, but salary records are missing. Repair the database before continuing.")
            self.stdout.write(self.style.WARNING(f"Database already has {count} employees; seed skipped."))
            return
        if existing:
            raise CommandError(f"Database already has {existing} employees. Seed only an empty database to avoid overwriting records.")
        rng = random.Random(42)
        employees, salaries = [], []
        for index in range(1, count + 1):
            first, last_base = rng.choice(FIRST_NAMES), rng.choice(LAST_NAMES); last = f"{last_base} {index:04d}"; country, currency = rng.choice(COUNTRIES); year = rng.randint(2016, 2025)
            employees.append(Employee(id=index, first_name=first, last_name=last, email=f"{first.lower()}.{last_base.lower()}{index}@acme.example", country=country, department=rng.choice(DEPARTMENTS), status="active" if rng.random() > .08 else "on_leave", start_date=date(year, 1, 15)))
        with transaction.atomic():
            Employee.objects.bulk_create(employees, batch_size=1000)
            for employee in Employee.objects.order_by("id"):
                currency = next(c for c in COUNTRIES if c[0] == employee.country)[1]
                salaries.append(SalaryRecord(employee=employee, amount=round(rng.uniform(55000, 180000), 2), currency=currency, pay_frequency="annual", effective_date=employee.start_date))
            SalaryRecord.objects.bulk_create(salaries, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f"Seeded {Employee.objects.count()} employees."))
