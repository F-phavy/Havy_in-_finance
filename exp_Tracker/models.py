from django.db import models
from datetime import datetime

class Account(models.Model):
    name = models.CharField(max_length=100)
    expense = models.FloatField(default=0)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    expense_list = models.ManyToManyField('Expense', blank=True)

class Expense(models.Model):
    name = models.CharField(max_length=200)    
    amount = models.FloatField(default=0)
    date = models.DateField(null=False, default=datetime.now)
    long_term = models.BooleanField(default=False)
    interest_rate = models.FloatField(default=0, null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    monthly_expenses = models.FloatField(default=0, null=True, blank=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.long_term and self.end_date:
            self.monthly_expenses = self.calculate_monthly_expense()
        else:
            self.monthly_expenses = 0
        super().save(*args, **kwargs) 

    def calculate_monthly_expense(self):
        if self.long_term and self.end_date:
            delta = self.end_date - self.date.date() if hasattr(self.date, 'date') else self.end_date - self.date
            months = delta.days / 30
            
            if months <= 0: 
                months = 1

            if not self.interest_rate or self.interest_rate == 0:
                return self.amount / months
            else:
                monthly_rate = (self.interest_rate / 100) / 12
                monthly_payment = (self.amount * monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
                monthly_payment = (self.amount * monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
                return monthly_payment
        
        return 0