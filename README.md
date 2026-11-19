# ACME Compensation Hub

ACME Compensation Hub is an internal HR tool for managing employee compensation and answering organization-wide pay questions. It replaces spreadsheet-based workflows with a searchable employee directory, salary history, audit events, and compensation insights.

**Live demo:** [utkarshsri288.pythonanywhere.com](https://utkarshsri288.pythonanywhere.com/). The hosted demo uses synthetic data and requires an account. Its administrator username is `acme_admin`; the unique password was chosen during deployment and is deliberately not stored in this repository. The PythonAnywhere free app needs monthly renewal and has limited CPU, disk, and worker capacity, so this is an assessment demo rather than a production payroll system.

## Product capabilities

- Username/password sign-in and API-enforced `ADMIN` and `HR_MANAGER` roles.
- Employee directory with search, country/department/status filters, sortable compensation, pagination, profiles, and CSV export for the current view.
- Compensation dashboard and insights with salary distributions and country/department comparisons.
- Salary updates with salary history and audit records.
- Administrator settings to create and deactivate HR Manager accounts and transfer the administrator role.
- Django Admin at `/admin/` and API health at `/api/health`.
- Deterministic seed data for 10,000 employees across multiple countries.

## Run locally

### Requirements

- Python 3.11 or newer
- Node.js 20 or newer and npm

Run commands from the repository root unless a step says otherwise. The app uses Django and SQLite for the backend and React/Vite for the frontend.

### Install and initialize

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r backend/requirements.txt
npm ci --prefix frontend
./.venv/bin/python backend/manage.py migrate
./.venv/bin/python backend/manage.py seed_employees
./.venv/bin/python backend/manage.py seed_hr_user
```

The local SQLite database defaults to `backend/db.sqlite3`. Set `DJANGO_DB_PATH` to use a different location. The employee seed creates 10,000 employees and matching salary records only in an empty employee table. Re-running it on a complete seed is a no-op; a partially populated table is rejected to protect existing data.

For a fresh local database, the demo sign-in is:

| Username | Password |
| --- | --- |
| `acme_admin` | `AcmeHR2026!` |

These credentials are **local development only**. They are not the live demo password. On the hosted deployment, `seed_hr_user` prompts for a unique password and does not print it. Never use real employee or salary data in this public demo.

### Start the backend and frontend

In terminal 1:

```bash
./.venv/bin/python backend/manage.py runserver 127.0.0.1:8000
```

In terminal 2:

```bash
npm run dev --prefix frontend
```

Open [http://localhost:5173](http://localhost:5173). Vite proxies API calls to Django at port 8000. The health check is [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health).

## Roles

| Capability | Administrator (`ADMIN`) | HR Manager (`HR_MANAGER`) |
| --- | :---: | :---: |
| View dashboard, insights, employee directory, and salary profiles | Yes | Yes |
| Edit compensation and export the current directory view | Yes | Yes |
| Create or deactivate HR Manager accounts | Yes | No |
| Transfer Administrator access to another active user | Yes | No |

Roles are stored in Django Groups and enforced by API permissions. New users receive the HR Manager role. Transferring administrator access demotes the previous administrator to HR Manager and promotes the selected active user as one transaction. Email is a contact field; login uses the username.

New account passwords must be at least eight characters and include uppercase, lowercase, a number, and a symbol; they cannot contain the username. The UI validates the password live and asks for confirmation, and the API applies the same validation.

## Run checks

```bash
./.venv/bin/python backend/manage.py check
./.venv/bin/python backend/manage.py test compensation
npm test --prefix frontend
npm run build --prefix frontend
```

The backend tests cover authentication, role permissions and transfers, password rules, seed safety, directory filtering/pagination/sorting, salary history, audit records, and CSV export. Frontend unit tests cover password validation; the production build runs TypeScript checks.

## Deployment

The current public demo runs on PythonAnywhere with Django serving the built React app and API, and SQLite stored in the account's persistent home directory. See [`docs/deploy-pythonanywhere.md`](docs/deploy-pythonanywhere.md) for a clean deployment walkthrough, WSGI configuration, static file mapping, and seed steps. The hosted app password is private and must not be committed.

PythonAnywhere's free tier has resource limits and requires the web app to be renewed monthly. SQLite is appropriate for this small, single-worker assessment demo; it is not a production payroll architecture. The seeded names, contact details, and salaries are synthetic. Fixed assessment FX rates are in `backend/compensation/currency.py`; salary amounts remain stored in each employee's local currency.

## Configuration notes

Local development defaults to `DJANGO_DEBUG=true`. For a deployment, set `DJANGO_DEBUG=false`, a private random `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, and the appropriate `DJANGO_DB_PATH`. Enable `DJANGO_TRUST_X_FORWARDED_PROTO=true` only behind a trusted proxy that sets the forwarded-protocol header. Never commit real `.env` files, database files, secrets, or production credentials.

## Troubleshooting

- **`No module named django`:** use `./.venv/bin/python` and install `backend/requirements.txt` as above.
- **Frontend says the API is unavailable:** confirm Django is running on port 8000 and `/api/health` returns `{"status":"ok"}`.
- **Hosted login rejects the local demo password:** expected. Use the unique password chosen on PythonAnywhere. If it is lost, open a Bash console on PythonAnywhere and run `cd ~/salary-management/backend && DJANGO_DEBUG=true DJANGO_DB_PATH=~/salary-management/backend/db.sqlite3 ../.venv/bin/python manage.py changepassword acme_admin`; enter the new password twice at the hidden prompts.
- **Seed rejects a partial database:** use a new SQLite path for a fresh demo. Back up an existing database before replacing it.
- **Port is already in use:** stop the process on 8000 or 5173; Vite expects Django on port 8000.

## Project guide

- [`docs/requirements.md`](docs/requirements.md) — persona, goals, MVP scope, and non-goals
- [`docs/architecture.md`](docs/architecture.md) — application shape, data model, API, and performance decisions
- [`docs/ai-usage.md`](docs/ai-usage.md) — where AI assisted and how outputs were checked
- [`docs/deploy-pythonanywhere.md`](docs/deploy-pythonanywhere.md) — hosted SQLite deployment steps
- [`planning/index.html`](planning/index.html) — visual product plan and interface references
- `backend/compensation/` — Django models, API, permissions, seed commands, and tests
- `frontend/src/pages/` and `frontend/src/components/` — React pages and reusable UI
