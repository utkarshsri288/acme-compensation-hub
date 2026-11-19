# Architecture and engineering decisions

## System shape

React/TypeScript (Vite) calls a Django REST Framework API. Django persists employees, one current salary record per employee, salary history, and audit events in SQLite. TanStack Query caches each screen's data by its parameters; a screen only mounts its own queries. Salary edits invalidate affected directory, profile, dashboard, and insights cache entries. The Vite development server proxies `/api` to Django.

```text
React pages → reusable UI components → /api → DRF views/serializers → Django ORM → SQLite
                                         └→ token auth + Django Group roles
```

## Data and access

- `Employee`: identity, country, department, status, start date.
- `SalaryRecord`: current amount, currency, pay frequency, effective date; one-to-one with employee.
- `SalaryHistory`: snapshots recorded when salary changes. The first edit also stores the original record.
- `AuditEvent`: action, changed field values, timestamp, and employee. The current schema does **not** store the actor; add actor attribution before real employee data is used.
- Django `User` + `Group`: `ADMIN` and `HR_MANAGER` roles. API permission classes enforce workspace membership and admin-only user management. Salary updates and admin transfers run in database transactions.

All reporting comparisons use annualized USD. Pay frequency and the fixed rates in `compensation/currency.py` feed SQL aggregates and salary sorting. Individual salary amounts remain in local currency. These fixed rates are an assessment assumption, not financial advice or a live FX feed.

## API used by the UI

| Route | Purpose |
| --- | --- |
| `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me` | Session lifecycle |
| `GET /api/dashboard` | Headcount, payroll, average, country count |
| `GET /api/insights?group_by=country\|department` | Grouped headcount, payroll, average |
| `GET /api/employees?search=&country=&department=&status=&sort=&direction=&page=&page_size=` | Filtered directory |
| `GET /api/employees/:id`, `PATCH /api/employees/:id` | Salary profile and update |
| `GET /api/employees/export?...` | CSV for current filtered page |
| `GET /api/admin/users`, `POST /api/admin/users`, `PATCH /api/admin/users/:id` | Admin user management |

## Scale and quality

Directory search, filters, sorting, pagination, and grouped compensation calculations happen in SQL. Country, department, and status are indexed. The directory returns 12 records by default in the UI, never 10,000 at once. Export uses the same filtered queryset and escapes spreadsheet formula prefixes. A deterministic seed command creates 10,000 employees and matching salary records in one transaction. Backend API tests cover permissions, calculations, updates, export, and seed behavior; frontend unit tests cover password rules.

## Current deployment boundary

The repository supplies a reproducible **local** two-server run path in `README.md`. A hosted deployment and video demo are still separate submission work. Before using real salary data, add actor attribution, stronger audit retention, SSO, backups, an appropriate production database, and an approved FX policy. Avoid treating the seeded SQLite database as real HR data.
