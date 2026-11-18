from django.urls import path
from .views import DashboardView, EmployeeDetailView, EmployeeListView, HealthView, InsightsView

urlpatterns = [
    path("health", HealthView.as_view()), path("dashboard", DashboardView.as_view()), path("insights", InsightsView.as_view()),
    path("employees", EmployeeListView.as_view()), path("employees/<int:pk>", EmployeeDetailView.as_view()),
]
