from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Employee, Payslip

MONTHS = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

MONTH_DATE_RANGES = {
    'January':   ('January 1-15',   'January 16-31'),
    'February':  ('February 1-15',  'February 16-28'),
    'March':     ('March 1-15',     'March 16-31'),
    'April':     ('April 1-15',     'April 16-30'),
    'May':       ('May 1-15',       'May 16-31'),
    'June':      ('June 1-15',      'June 16-30'),
    'July':      ('July 1-15',      'July 16-31'),
    'August':    ('August 1-15',    'August 16-31'),
    'September': ('September 1-15', 'September 16-30'),
    'October':   ('October 1-15',   'October 16-31'),
    'November':  ('November 1-15',  'November 16-30'),
    'December':  ('December 1-15',  'December 16-31'),
}

PAG_IBIG = 100.0
PHILHEALTH_RATE = 0.04
SSS_RATE = 0.045
TAX_RATE = 0.2


# ── EMPLOYEES ────────────────────────────────────────────────────────────────

def employees(request):
    all_employees = Employee.objects.all()
    return render(request, 'payroll_app/employees.html', {'employees': all_employees})


def create_employee(request):
    if request.method == 'POST':
        name      = request.POST.get('name', '').strip()
        id_number = request.POST.get('id_number', '').strip()
        rate      = request.POST.get('rate', '').strip()
        allowance = request.POST.get('allowance', '').strip()

        if not name or not id_number or not rate:
            messages.error(request, 'Name, ID Number, and Rate are required.')
            return render(request, 'payroll_app/create_employee.html')

        if Employee.objects.filter(pk=id_number).exists():
            messages.error(request, f'Employee with ID {id_number} already exists.')
            return render(request, 'payroll_app/create_employee.html')

        Employee.objects.create(
            name=name,
            id_number=id_number,
            rate=float(rate),
            allowance=float(allowance) if allowance else None,
            overtime_pay=0.0,
        )
        messages.success(request, f'Employee {name} created successfully.')
        return redirect('employees')

    return render(request, 'payroll_app/create_employee.html')


def update_employee(request, id_number):
    employee = get_object_or_404(Employee, pk=id_number)

    if request.method == 'POST':
        employee.name      = request.POST.get('name', '').strip()
        employee.rate      = float(request.POST.get('rate', employee.rate))
        allowance          = request.POST.get('allowance', '').strip()
        employee.allowance = float(allowance) if allowance else None
        employee.save()
        messages.success(request, f'Employee {employee.name} updated.')
        return redirect('employees')

    return render(request, 'payroll_app/update_employee.html', {'employee': employee})


def delete_employee(request, id_number):
    employee = get_object_or_404(Employee, pk=id_number)
    employee.delete()
    messages.success(request, 'Employee deleted.')
    return redirect('employees')


def add_overtime(request, id_number):
    employee = get_object_or_404(Employee, pk=id_number)

    if request.method == 'POST':
        hours = request.POST.get('overtime_hours', '').strip()
        if hours:
            ot_pay = (employee.rate / 160) * 1.5 * float(hours)
            employee.overtime_pay = (employee.overtime_pay or 0.0) + ot_pay
            employee.save()
            messages.success(request, f'Overtime of {ot_pay:.2f} added to {employee.name}.')
        else:
            messages.error(request, 'Please enter overtime hours.')

    return redirect('employees')


# ── PAYSLIPS ─────────────────────────────────────────────────────────────────

def payslips(request):
    all_employees = Employee.objects.all()
    all_payslips  = Payslip.objects.select_related('id_number').all()
    error_message = None

    if request.method == 'POST':
        payroll_for = request.POST.get('payroll_for', '')
        month       = request.POST.get('month', '')
        year        = request.POST.get('year', '').strip()
        cycle       = request.POST.get('cycle', '')

        if not month or not year or not cycle:
            error_message = 'Please fill in all fields.'
        else:
            cycle      = int(cycle)
            date_range = MONTH_DATE_RANGES[month][cycle - 1]
            targets    = list(all_employees) if payroll_for == 'all' else [get_object_or_404(Employee, pk=payroll_for)]
            skipped    = []

            for emp in targets:
                already_exists = Payslip.objects.filter(
                    id_number=emp, month=month, year=year, pay_cycle=cycle
                ).exists()

                if already_exists:
                    skipped.append(emp.id_number)
                    continue

                rate      = emp.rate
                allowance = emp.allowance or 0.0
                overtime  = emp.overtime_pay or 0.0
                half_rate = rate / 2

                if cycle == 1:
                    pag_ibig   = PAG_IBIG
                    philhealth = 0.0
                    sss        = 0.0
                    tax        = (half_rate + allowance + overtime - pag_ibig) * TAX_RATE
                    total_pay  = (half_rate + allowance + overtime - pag_ibig) - tax
                else:
                    pag_ibig   = 0.0
                    philhealth = rate * PHILHEALTH_RATE
                    sss        = rate * SSS_RATE
                    tax        = (half_rate + allowance + overtime - philhealth - sss) * TAX_RATE
                    total_pay  = (half_rate + allowance + overtime - philhealth - sss) - tax

                Payslip.objects.create(
                    id_number=emp,
                    month=month,
                    date_range=date_range,
                    year=year,
                    pay_cycle=cycle,
                    rate=rate,
                    earnings_allowance=allowance,
                    deductions_tax=tax,
                    deductions_health=philhealth,
                    pag_ibig=pag_ibig,
                    sss=sss,
                    overtime=overtime,
                    total_pay=total_pay,
                )
                emp.resetOvertime()

            if skipped:
                error_message = f'Payslip already exists for: {", ".join(skipped)}. Skipped.'
            else:
                messages.success(request, 'Payslip(s) generated successfully.')

        all_payslips = Payslip.objects.select_related('id_number').all()

    context = {
        'employees':     all_employees,
        'payslips':      all_payslips,
        'months':        MONTHS,
        'error_message': error_message,
    }
    return render(request, 'payroll_app/payslips.html', context)


def view_payslip(request, pk):
    payslip = get_object_or_404(Payslip, pk=pk)
    return render(request, 'payroll_app/view_payslip.html', {'payslip': payslip})