# Architecture & Engineering Notes

## Shape

The first implementation uses a small modular monolith: a REST API and a React client backed by SQLite for local reproducibility. The boundaries are intentionally portable to PostgreSQL and a managed deployment later.

```text
React UI ──HTTP/JSON──> API routes ──> service/query modules ──> SQLite
                           │
                           └── audit_events (append-only)
```

## Data model

- `employees`: identity and organization fields.
- `salary_records`: one current salary record per employee in the MVP, with local currency and effective date.
- `audit_events`: actor, action, changed fields, timestamp, and target employee.

The API returns annualized amounts for comparisons using pay-frequency rules. Original salary and currency remain intact for editing and auditability.

## API contract

- `GET /api/health`
- `GET /api/dashboard?country=&department=`
- `GET /api/employees?search=&country=&department=&status=&page=&page_size=`
- `GET /api/employees/:id`
- `PATCH /api/employees/:id/salary`
- `GET /api/analysis?group_by=country|department`
- `GET /api/employees/export?...` (CSV)

## Performance choices

Search/filter/sort/pagination happen in SQL. Indexes cover employee country, department, status, and salary effective date. Analysis uses grouped SQL queries instead of loading all employees into application memory. Seed data is generated in a transaction.

## Quality strategy

Unit tests focus on annualization, validation, filter parsing, and audit behavior. API tests exercise the critical read/update paths against an isolated database. A small frontend test suite will cover formatting and key interaction states.

## Deployment path

For the assessment, a single process can serve the built frontend and API with a file-backed database. For production: PostgreSQL, object storage for exports, SSO/OIDC, secrets manager, TLS, structured logs, backups, and an external FX provider.
