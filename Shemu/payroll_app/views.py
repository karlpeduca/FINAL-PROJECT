from django.shortcuts import render, get_object_or_404, redirect
from .models import Employee, Payslip

def employees(request):
    all_employees = Employee.objects.all()
    return render(request, 'payroll_app/employees.html', {'employees': all_employees})