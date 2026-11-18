from django.db.models import Avg, Count, F, Q, Sum, Value, Case, When, DecimalField, ExpressionWrapper
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Employee, SalaryRecord, AuditEvent, SalaryHistory
from .serializers import EmployeeSerializer, SalaryUpdateSerializer

FX = {"USD": 1, "INR": .012, "GBP": 1.27, "EUR": 1.09, "SGD": .74, "AUD": .65}
def annualized_usd_expression():
    frequency = Case(When(salary__pay_frequency="monthly", then=Value(12)), When(salary__pay_frequency="biweekly", then=Value(26)), When(salary__pay_frequency="weekly", then=Value(52)), default=Value(1), output_field=DecimalField())
    fx = Case(*[When(salary__currency=key, then=Value(value)) for key, value in FX.items()], output_field=DecimalField())
    return ExpressionWrapper(F("salary__amount") * frequency * fx, output_field=DecimalField(max_digits=18, decimal_places=2))

class HealthView(APIView):
    def get(self, request): return Response({"status": "ok"})

class EmployeeListView(ListAPIView):
    serializer_class = EmployeeSerializer
    def get_queryset(self):
        qs = Employee.objects.select_related("salary").all().order_by("last_name", "first_name")
        for key in ("country", "department", "status"):
            if self.request.query_params.get(key): qs = qs.filter(**{key: self.request.query_params[key]})
        search = self.request.query_params.get("search")
        if search: qs = qs.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(email__icontains=search))
        return qs
    def list(self, request, *args, **kwargs):
        qs = self.get_queryset(); page = max(int(request.query_params.get("page", 1)), 1); size = min(max(int(request.query_params.get("page_size", 25)), 1), 100); total = qs.count(); start = (page - 1) * size
        return Response({"data": self.get_serializer(qs[start:start + size], many=True).data, "meta": {"page": page, "page_size": size, "total": total, "pages": (total + size - 1) // size}})

class EmployeeDetailView(RetrieveAPIView):
    queryset = Employee.objects.select_related("salary").prefetch_related("salary_history", "audit_events")
    serializer_class = EmployeeSerializer
    def patch(self, request, *args, **kwargs):
        employee = self.get_object(); salary = employee.salary; serializer = SalaryUpdateSerializer(salary, data=request.data, partial=True); serializer.is_valid(raise_exception=True)
        before = {field: str(getattr(salary, field)) for field in serializer.validated_data}; old = {field: str(getattr(salary, field)) for field in serializer.validated_data}; serializer.save()
        SalaryHistory.objects.create(employee=employee, amount=salary.amount, currency=salary.currency, pay_frequency=salary.pay_frequency, effective_date=salary.effective_date, reason=request.data.get("reason", "Salary update"))
        AuditEvent.objects.create(employee=employee, action="salary_updated", changed_fields={field: {"before": old[field], "after": before[field]} for field in before})
        return Response(EmployeeSerializer(employee).data, status=status.HTTP_200_OK)

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
