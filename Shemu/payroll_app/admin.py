from django.contrib import admin
from .models import Employee, Payslip, Profile, AuditLog

admin.site.register(Employee)
admin.site.register(Payslip)
admin.site.register(Profile)
admin.site.register(AuditLog)