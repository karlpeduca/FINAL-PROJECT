from django.contrib import admin
from .models import Employee, Payslip, AuditLog

admin.site.register(Employee)
admin.site.register(Payslip)
admin.site.register(AuditLog)