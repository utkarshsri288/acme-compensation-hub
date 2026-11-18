from rest_framework import serializers
from .models import Employee, SalaryRecord

class SalarySerializer(serializers.ModelSerializer):
    annualized = serializers.SerializerMethodField()
    class Meta:
        model = SalaryRecord
        fields = ["amount", "currency", "pay_frequency", "effective_date", "updated_at", "annualized"]
    def get_annualized(self, obj): return obj.annualized()

class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    salary = SalarySerializer(read_only=True)
    annualized_usd = serializers.SerializerMethodField()
    class Meta:
        model = Employee
        fields = ["id", "full_name", "first_name", "last_name", "email", "country", "department", "status", "start_date", "salary", "annualized_usd"]
    def get_annualized_usd(self, obj):
        rates = {"USD": 1, "INR": .012, "GBP": 1.27, "EUR": 1.09, "SGD": .74, "AUD": .65}
        return round(float(obj.salary.annualized()) * rates[obj.salary.currency], 2)

class SalaryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryRecord
        fields = ["amount", "currency", "pay_frequency", "effective_date"]
    def validate_amount(self, value):
        if value <= 0: raise serializers.ValidationError("Salary must be greater than zero.")
        return value
