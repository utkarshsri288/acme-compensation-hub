import os
import sys

username = "<pythonanywhere-username>"
project_root = f"/home/{username}/salary-management/backend"
if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
os.environ["DJANGO_DEBUG"] = "false"
os.environ["DJANGO_SECRET_KEY"] = "<generate-a-long-random-secret>"
os.environ["DJANGO_ALLOWED_HOSTS"] = f"{username}.pythonanywhere.com"
os.environ["DJANGO_DB_PATH"] = f"/home/{username}/salary-management/backend/db.sqlite3"
os.environ["DJANGO_SERVE_FRONTEND"] = "true"

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
