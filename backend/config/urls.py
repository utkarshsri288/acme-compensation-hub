import os
from pathlib import Path

from django.contrib import admin
from django.http import FileResponse, Http404
from django.urls import include, path


def frontend_index(request):
    index_file = Path(__file__).resolve().parents[2] / "frontend" / "dist" / "index.html"
    if not index_file.is_file():
        raise Http404("Frontend build not found. Build frontend before enabling DJANGO_SERVE_FRONTEND.")
    return FileResponse(index_file.open("rb"), content_type="text/html; charset=utf-8")


urlpatterns = [path("admin/", admin.site.urls), path("api/", include("compensation.urls"))]
if os.getenv("DJANGO_SERVE_FRONTEND", "false").lower() == "true":
    urlpatterns.append(path("", frontend_index))
