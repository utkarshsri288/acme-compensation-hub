# Free SQLite deployment on PythonAnywhere

This guide deploys the assessment demo as one Django WSGI app. Django serves `/` with the React build, `/api/` with DRF, and `/admin/` with Django Admin. SQLite stays in the account's home directory. Use synthetic assessment data only.

PythonAnywhere's free account currently includes SQLite, but has 512 MiB disk, 100 CPU seconds, one web app with one worker, and a one-month web-app expiry. This is a temporary demo target; check the provider's current [free account limits](https://help.pythonanywhere.com/pages/FreeAccountsFeatures) before deploying.

## 1. Build the React UI

From the project root, with Node/npm installed:

```bash
npm ci --prefix frontend
npm run build:pythonanywhere --prefix frontend
```

The build uses `/static/` as its asset base. Include `frontend/dist/` when uploading the project; Django collects its assets in the next steps.

## 2. Upload and configure the PythonAnywhere web app

Create a PythonAnywhere free account and a manual-configuration web app using Python 3.11. Upload the project so that `manage.py` is at:

```text
/home/<pythonanywhere-username>/salary-management/backend/manage.py
```

In a PythonAnywhere Bash console:

```bash
cd ~/salary-management
python3.11 -m venv .venv
./.venv/bin/pip install -r backend/requirements.txt
```

Edit the WSGI file linked from the Web tab so it points at the backend folder:

```python
import os
import sys

project_root = "/home/<pythonanywhere-username>/salary-management/backend"
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
os.environ["DJANGO_DEBUG"] = "false"
os.environ["DJANGO_SECRET_KEY"] = "<generate-a-long-random-secret>"
os.environ["DJANGO_ALLOWED_HOSTS"] = "<pythonanywhere-username>.pythonanywhere.com"
os.environ["DJANGO_DB_PATH"] = "/home/<pythonanywhere-username>/salary-management/backend/db.sqlite3"
os.environ["DJANGO_SERVE_FRONTEND"] = "true"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Replace each placeholder with your own account values. Keep the secret private. The database path is inside your persistent home directory so restarts preserve it.

## 3. Migrate, seed, and collect static assets

```bash
cd ~/salary-management
./.venv/bin/python backend/manage.py migrate --noinput
./.venv/bin/python backend/manage.py seed_employees
./.venv/bin/python backend/manage.py seed_hr_user
./.venv/bin/python backend/manage.py collectstatic --noinput
```

In the PythonAnywhere Web tab, set the virtualenv to `/home/<username>/salary-management/.venv`, then add this static files mapping:

| URL | Directory |
| --- | --- |
| `/static/` | `/home/<username>/salary-management/backend/staticfiles/` |

Reload the web app. The React UI is at `https://<username>.pythonanywhere.com/`, Django Admin at `/admin/`, and API health at `/api/health`.

With `DJANGO_DEBUG=false`, `seed_hr_user` prompts for a unique app admin password and confirmation without echoing either value. Use `acme_admin` with the password you choose to sign in. Local development retains the README demo credentials. Never use real compensation records on this free demo deployment.
