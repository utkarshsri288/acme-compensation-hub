import csv
import re
from django.http import HttpResponse
from django.db import transaction
from django.db.models import Avg, Count, F, Q, Sum, Value, Case, When, DecimalField, ExpressionWrapper
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .currency import FX_RATES
from .models import Employee, SalaryRecord, AuditEvent, SalaryHistory
from .serializers import EmployeeSerializer, EmployeeDetailSerializer, SalaryUpdateSerializer
from .roles import ADMIN, HR_MANAGER, WORKSPACE_ROLES, IsWorkspaceAdmin, role_for, user_payload
from .passwords import password_validation_errors

def annualized_usd_expression():
    frequency = Case(When(salary__pay_frequency="monthly", then=Value(12)), When(salary__pay_frequency="biweekly", then=Value(26)), When(salary__pay_frequency="weekly", then=Value(52)), default=Value(1), output_field=DecimalField())
    fx = Case(*[When(salary__currency=key, then=Value(value)) for key, value in FX_RATES.items()], output_field=DecimalField())
    return ExpressionWrapper(F("salary__amount") * frequency * fx, output_field=DecimalField(max_digits=18, decimal_places=2))

class HealthView(APIView):
    permission_classes = [AllowAny]
    def get(self, request): return Response({"status": "ok"})

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        if not isinstance(username, str) or not isinstance(password, str):
            return Response({"detail": "Username and password must be text."}, status=status.HTTP_400_BAD_REQUEST)
        username = username.strip().lower()
        user = authenticate(username=username, password=password)
        if not user or role_for(user) is None:
            return Response({"detail": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": user_payload(user)})

class LogoutView(APIView):
    def post(self, request):
        if request.auth: request.auth.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class MeView(APIView):
    def get(self, request): return Response(user_payload(request.user))

class AdminUserListView(APIView):
    permission_classes = [IsWorkspaceAdmin]
    def get(self, request):
        User = get_user_model()
        users = User.objects.filter(groups__name__in=WORKSPACE_ROLES).distinct().order_by("first_name", "last_name", "username")
        return Response([user_payload(user) for user in users])
    def post(self, request):
        User = get_user_model()
        username = request.data.get("username", "")
        email = request.data.get("email", "")
        name = request.data.get("name", "")
        password = request.data.get("password", "")
        if not all(isinstance(value, str) for value in (username, email, name, password)):
            return Response({"detail": "Username, name, email and password must be text."}, status=status.HTTP_400_BAD_REQUEST)
        username = username.strip().lower()
        email = email.strip().lower()
        name = name.strip()
        if not re.fullmatch(r"[a-z][a-z0-9_.-]{2,29}", username):
            return Response({"detail": "Username must be 3–30 characters using letters, numbers, _, . or -."}, status=status.HTTP_400_BAD_REQUEST)
        if not name:
            return Response({"detail": "Full name is required."}, status=status.HTTP_400_BAD_REQUEST)
        password_errors = password_validation_errors(password, username)
        if password_errors:
            return Response({"detail": "Password needs " + ", ".join(password_errors) + "."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_email(email)
        except ValidationError:
            return Response({"detail": "Enter a valid email address."}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username__iexact=username).exists():
            return Response({"detail": "Username is already taken."}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email__iexact=email).exists():
            return Response({"detail": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        parts = name.split(" ", 1)
        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, first_name=parts[0], last_name=parts[1] if len(parts) > 1 else "", password=password, is_staff=False)
            user.groups.add(Group.objects.get(name=HR_MANAGER))
        return Response(user_payload(user), status=status.HTTP_201_CREATED)

class AdminUserDetailView(APIView):
    permission_classes = [IsWorkspaceAdmin]
    @transaction.atomic
    def patch(self, request, pk):
        User = get_user_model()
        try: user = User.objects.filter(groups__name__in=WORKSPACE_ROLES).distinct().get(pk=pk)
        except User.DoesNotExist: return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        if user == request.user: return Response({"detail": "You cannot modify or transfer your own admin account."}, status=status.HTTP_400_BAD_REQUEST)
        if request.data.get("transfer_admin") is True:
            if not user.is_active:
                return Response({"detail": "Activate the user before transferring administrator access."}, status=status.HTTP_400_BAD_REQUEST)
            admin_group = Group.objects.get(name=ADMIN)
            hr_group = Group.objects.get(name=HR_MANAGER)
            user.groups.set([admin_group])
            request.user.groups.set([hr_group])
            user.is_staff = True; user.is_superuser = True; user.save(update_fields=["is_staff", "is_superuser"])
            request.user.is_staff = False; request.user.is_superuser = False; request.user.save(update_fields=["is_staff", "is_superuser"])
            return Response({"transferred": True, **user_payload(user)})
        if "is_active" not in request.data or not isinstance(request.data["is_active"], bool):
            return Response({"detail": "Provide is_active as true or false."}, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = request.data["is_active"]
        user.save(update_fields=["is_active"])
        return Response(user_payload(user))

class EmployeeListView(ListAPIView):
    serializer_class = EmployeeSerializer
    def get_queryset(self):
        qs = Employee.objects.select_related("salary").all().order_by("last_name", "first_name")
        for key in ("country", "department", "status"):
            if self.request.query_params.get(key): qs = qs.filter(**{key: self.request.query_params[key]})
        search = self.request.query_params.get("search")
        if search: qs = qs.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(email__icontains=search))
        sort = self.request.query_params.get("sort", "name")
        direction = "-" if self.request.query_params.get("direction", "asc") == "desc" else ""
        sort_fields = {"name": "last_name", "department": "department", "country": "country", "salary": "annual_usd", "status": "status"}
        if sort == "salary":
            qs = qs.annotate(annual_usd=annualized_usd_expression())
        qs = qs.order_by(f"{direction}{sort_fields.get(sort, 'last_name')}", "first_name", "id")
        return qs
    def list(self, request, *args, **kwargs):
        try:
            page = max(int(request.query_params.get("page", 1)), 1)
            size = min(max(int(request.query_params.get("page_size", 25)), 1), 100)
        except ValueError:
            return Response({"detail": "Invalid page or page size."}, status=status.HTTP_400_BAD_REQUEST)
        qs = self.get_queryset(); total = qs.count(); start = (page - 1) * size
        return Response({"data": self.get_serializer(qs[start:start + size], many=True).data, "meta": {"page": page, "page_size": size, "total": total, "pages": (total + size - 1) // size}})

class EmployeeExportView(EmployeeListView):
    def get(self, request, *args, **kwargs):
        try:
            page = max(int(request.query_params.get("page", 1)), 1)
            size = min(max(int(request.query_params.get("page_size", 12)), 1), 100)
        except ValueError:
            return Response({"detail": "Invalid page or page size."}, status=status.HTTP_400_BAD_REQUEST)
        start = (page - 1) * size
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="acme-employees-page.csv"'
        writer = csv.writer(response)
        writer.writerow(["Employee ID", "Name", "Email", "Department", "Country", "Status", "Salary amount", "Currency", "Pay frequency", "Annualized USD"])
        for employee in self.get_queryset()[start:start + size]:
            salary = employee.salary
            values = [employee.id, employee.full_name, employee.email, employee.department, employee.country, employee.status, salary.amount, salary.currency, salary.pay_frequency, EmployeeSerializer(employee).data["annualized_usd"]]
            writer.writerow(["'" + value if isinstance(value, str) and value.startswith(("=", "+", "-", "@")) else value for value in values])
        return response

class EmployeeDetailView(RetrieveAPIView):
    queryset = Employee.objects.select_related("salary")
    serializer_class = EmployeeDetailSerializer
    def retrieve(self, request, *args, **kwargs):
        employee = self.get_object()
        return Response(self.get_serializer(employee).data)

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        employee = self.get_object(); salary = employee.salary; serializer = SalaryUpdateSerializer(salary, data=request.data, partial=True); serializer.is_valid(raise_exception=True)
        reason = request.data.get("reason", "Salary update")
        if not isinstance(reason, str) or len(reason.strip()) > 200:
            return Response({"detail": "Reason must be text up to 200 characters."}, status=status.HTTP_400_BAD_REQUEST)
        reason = reason.strip() or "Salary update"
        old = {field: str(getattr(salary, field)) for field in serializer.validated_data}
        if not old or all(old[field] == str(value) for field, value in serializer.validated_data.items()):
            return Response({"detail": "No salary fields changed."}, status=status.HTTP_400_BAD_REQUEST)
        if not employee.salary_history.exists():
            SalaryHistory.objects.create(employee=employee, amount=salary.amount, currency=salary.currency, pay_frequency=salary.pay_frequency, effective_date=salary.effective_date, reason="Original record")
        serializer.save(); after = {field: str(getattr(salary, field)) for field in serializer.validated_data}
        SalaryHistory.objects.create(employee=employee, amount=salary.amount, currency=salary.currency, pay_frequency=salary.pay_frequency, effective_date=salary.effective_date, reason=reason)
        AuditEvent.objects.create(employee=employee, action="salary_updated", changed_fields={field: {"before": old[field], "after": after[field]} for field in after})
        return Response(self.get_serializer(employee).data, status=status.HTTP_200_OK)

class DashboardView(APIView):
    def get(self, request):
        qs = Employee.objects.select_related("salary"); country = request.query_params.get("country"); department = request.query_params.get("department")
        if country: qs = qs.filter(country=country)
        if department: qs = qs.filter(department=department)
        values = qs.annotate(annual_usd=annualized_usd_expression()).aggregate(headcount=Count("id"), payroll_usd=Sum("annual_usd"), average_salary_usd=Avg("annual_usd"))
        return Response({"headcount": values["headcount"], "payroll_usd": round(float(values["payroll_usd"] or 0), 2), "average_salary_usd": round(float(values["average_salary_usd"] or 0), 2), "countries": qs.values("country").distinct().count(), "reporting_currency": "USD"})

class InsightsView(APIView):
    def get(self, request):
        field = request.query_params.get("group_by", "country"); field = field if field in ("country", "department") else "country"; rows = Employee.objects.select_related("salary").annotate(annual_usd=annualized_usd_expression()).values(field).annotate(headcount=Count("id"), payroll_usd=Sum("annual_usd"), average_salary_usd=Avg("annual_usd")).order_by("-payroll_usd")
        return Response([{**row, "group_name": row.pop(field), "payroll_usd": round(float(row["payroll_usd"] or 0), 2), "average_salary_usd": round(float(row["average_salary_usd"] or 0), 2)} for row in rows])
