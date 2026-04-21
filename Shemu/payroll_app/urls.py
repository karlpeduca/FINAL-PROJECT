from django.urls import path
from . import views

urlpatterns = [
    path('', views.employees, name='employees'),
    path('employees/new/', views.create_employee, name='create_employee'),
    path('employees/<str:id_number>/update/', views.update_employee, name='update_employee'),
    path('employees/<str:id_number>/delete/', views.delete_employee, name='delete_employee'),
    path('employees/<str:id_number>/overtime/', views.add_overtime, name='add_overtime'),
    path('payslips/', views.payslips, name='payslips'),
    path('payslips/<int:pk>/', views.view_payslip, name='view_payslip'),
]