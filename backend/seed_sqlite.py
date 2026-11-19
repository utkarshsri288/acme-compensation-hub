"""Create a dependency-free local demo SQLite database for the assessment.

The schema mirrors the Django model tables, so it can be used immediately for
local inspection and replaced with `manage.py migrate` + `seed_employees` when
the Python dependencies are installed.
"""
import random
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB = Path(__file__).with_name("db.sqlite3")
COUNTRIES = [("United States", "USD"), ("India", "INR"), ("United Kingdom", "GBP"), ("Germany", "EUR"), ("Singapore", "SGD"), ("Australia", "AUD")]
DEPARTMENTS = ["Engineering", "People", "Finance", "Sales", "Marketing", "Operations", "Legal"]
FIRST = ["Avery", "Maya", "Noah", "Priya", "Lucas", "Sofia", "Ethan", "Amara", "Liam", "Zoe", "Arjun", "Mila"]
LAST = ["Patel", "Nguyen", "Morgan", "Singh", "Garcia", "Chen", "Williams", "Kumar", "Smith", "Brown", "Martin", "Mehta"]

conn = sqlite3.connect(DB)
conn.executescript("""
CREATE TABLE IF NOT EXISTS compensation_employee (id INTEGER PRIMARY KEY, first_name VARCHAR(80) NOT NULL, last_name VARCHAR(80) NOT NULL, email VARCHAR(254) NOT NULL UNIQUE, country VARCHAR(80) NOT NULL, department VARCHAR(80) NOT NULL, status VARCHAR(20) NOT NULL, start_date DATE NOT NULL, created_at DATETIME NOT NULL);
CREATE INDEX IF NOT EXISTS employee_country_idx ON compensation_employee(country);
CREATE INDEX IF NOT EXISTS employee_department_idx ON compensation_employee(department);
CREATE INDEX IF NOT EXISTS employee_status_idx ON compensation_employee(status);
CREATE TABLE IF NOT EXISTS compensation_salaryrecord (id INTEGER PRIMARY KEY, amount DECIMAL(14,2) NOT NULL, currency VARCHAR(3) NOT NULL, pay_frequency VARCHAR(12) NOT NULL, effective_date DATE NOT NULL, updated_at DATETIME NOT NULL, employee_id INTEGER NOT NULL UNIQUE REFERENCES compensation_employee(id));
CREATE TABLE IF NOT EXISTS compensation_salaryhistory (id INTEGER PRIMARY KEY, amount DECIMAL(14,2) NOT NULL, currency VARCHAR(3) NOT NULL, pay_frequency VARCHAR(12) NOT NULL, effective_date DATE NOT NULL, reason VARCHAR(200) NOT NULL, created_at DATETIME NOT NULL, employee_id INTEGER NOT NULL REFERENCES compensation_employee(id));
CREATE TABLE IF NOT EXISTS compensation_auditevent (id INTEGER PRIMARY KEY, action VARCHAR(80) NOT NULL, changed_fields TEXT NOT NULL, created_at DATETIME NOT NULL, employee_id INTEGER NOT NULL REFERENCES compensation_employee(id));
""")
existing_count = conn.execute("SELECT COUNT(*) FROM compensation_employee").fetchone()[0]
if existing_count >= 10000:
    # Upgrade an already-created demo database so every visible employee name is distinct.
    with conn:
        for index in range(1, 10001):
            last_base = LAST[(index - 1) // len(FIRST) % len(LAST)]
            conn.execute("UPDATE compensation_employee SET last_name = ? WHERE id = ?", (f"{last_base} {index:04d}", index))
elif existing_count < 10000:
    rng = random.Random(42); now = datetime.now(timezone.utc).isoformat(); employees = []; salaries = []
    for index in range(1, 10001):
        first, last_base = rng.choice(FIRST), rng.choice(LAST); last = f"{last_base} {index:04d}"; country, currency = rng.choice(COUNTRIES); year = rng.randint(2016, 2025)
        employees.append((index, first, last, f"{first.lower()}.{last_base.lower()}{index}@acme.example", country, rng.choice(DEPARTMENTS), "active" if rng.random() > .08 else "on_leave", f"{year}-01-15", now))
        salaries.append((index, round(rng.uniform(55000, 180000), 2), currency, "annual", f"{year}-01-15", now, index))
    with conn:
        conn.executemany("INSERT INTO compensation_employee VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", employees)
        conn.executemany("INSERT INTO compensation_salaryrecord VALUES (?, ?, ?, ?, ?, ?, ?)", salaries)
print(f"Demo database ready: {DB} ({conn.execute('SELECT COUNT(*) FROM compensation_employee').fetchone()[0]} employees)")
conn.close()
