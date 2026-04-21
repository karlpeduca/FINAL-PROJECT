from django.shortcuts import render, get_object_or_404, redirect
from .models import Employee, Payslip

# Create your views here.
def base(request):
    return render(request,'payroll_app/base.html')
