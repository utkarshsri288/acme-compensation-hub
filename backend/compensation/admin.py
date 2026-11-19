from django.contrib import admin

from .models import AuditEvent, Employee, SalaryHistory, SalaryRecord


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "email", "department", "country", "status")
    list_filter = ("status", "country", "department")
    search_fields = ("first_name", "last_name", "email")
    ordering = ("last_name", "first_name")
    list_per_page = 50


@admin.register(SalaryRecord)
class SalaryRecordAdmin(admin.ModelAdmin):
    list_display = ("employee", "amount", "currency", "pay_frequency", "effective_date", "updated_at")
    list_filter = ("currency", "pay_frequency")
    search_fields = ("employee__first_name", "employee__last_name", "employee__email")
    autocomplete_fields = ("employee",)
    list_per_page = 50


@admin.register(SalaryHistory)
class SalaryHistoryAdmin(admin.ModelAdmin):
    list_display = ("employee", "amount", "currency", "pay_frequency", "effective_date", "created_at")
    list_filter = ("currency", "pay_frequency")
    search_fields = ("employee__first_name", "employee__last_name", "employee__email")
    autocomplete_fields = ("employee",)
    list_per_page = 50
    readonly_fields = ("employee", "amount", "currency", "pay_frequency", "effective_date", "reason", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("employee", "action", "created_at")
    list_filter = ("action",)
    search_fields = ("employee__first_name", "employee__last_name", "employee__email")
    autocomplete_fields = ("employee",)
    list_per_page = 50
    readonly_fields = ("employee", "action", "changed_fields", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
