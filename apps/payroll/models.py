"""
Payroll application models.
"""
from django.db import models
from decimal import Decimal
from auditlog.registry import auditlog


class Payroll(models.Model):
    """
    Payroll model for managing employee salaries and payslips.
    """
    employee = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='payrolls'
    )
    month = models.IntegerField()  # 1-12
    year = models.IntegerField()
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    allowances = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payroll'
        ordering = ['-year', '-month', 'employee__first_name']
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'month', 'year'],
                name='uq_payroll_employee_month_year',
            ),
        ]
        indexes = [
            models.Index(fields=['employee'], name='idx_payroll_employee'),
            models.Index(fields=['year', 'month'], name='idx_payroll_year_month'),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.month}/{self.year}"

    def calculate_overtime_pay(self):
        """
        Calculate overtime pay based on the formula:
        overtime_pay = (basic_salary / 30 / 8) * 1.5 * overtime_hours
        """
        if self.basic_salary and self.overtime_hours:
            hourly_rate = Decimal(str(self.basic_salary)) / Decimal('30') / Decimal('8')
            overtime_rate = hourly_rate * Decimal('1.5')
            return overtime_rate * Decimal(str(self.overtime_hours))
        return Decimal('0')

    def calculate_net_salary(self):
        """
        Calculate net salary:
        net_salary = basic_salary + allowances + overtime_pay - deductions
        """
        return Decimal(str(self.basic_salary)) + Decimal(str(self.allowances)) + \
               Decimal(str(self.overtime_pay)) - Decimal(str(self.deductions))

    def save(self, *args, **kwargs):
        """Override save to calculate net_salary before saving."""
        if not self.net_salary:
            self.net_salary = self.calculate_net_salary()
        super().save(*args, **kwargs)

    @property
    def month_name(self):
        """Return the month name."""
        from datetime import datetime
        return datetime(self.year, self.month, 1).strftime('%B')


# Register model for audit logging
auditlog.register(Payroll)
