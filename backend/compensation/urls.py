from django.urls import path
from .views import AdminUserDetailView, AdminUserListView, DashboardView, EmployeeDetailView, EmployeeExportView, EmployeeListView, HealthView, InsightsView, LoginView, LogoutView, MeView

urlpatterns = [
    path("health", HealthView.as_view()), path("auth/login", LoginView.as_view()), path("auth/logout", LogoutView.as_view()), path("auth/me", MeView.as_view()), path("admin/users", AdminUserListView.as_view()), path("admin/users/<int:pk>", AdminUserDetailView.as_view()), path("dashboard", DashboardView.as_view()), path("insights", InsightsView.as_view()),
    path("employees", EmployeeListView.as_view()), path("employees/export", EmployeeExportView.as_view()), path("employees/<int:pk>", EmployeeDetailView.as_view()),
]
