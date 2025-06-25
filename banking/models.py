# banking/models.py
from django.db import models
from django.conf import settings

from accounts.models import CustomUser

class BankAccount(models.Model):
    ACCOUNT_TYPES = (
        ('checking', 'Checking'),
        ('savings', 'Savings'),
        ('business', 'Business'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    account_number = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s {self.account_type} Account"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
        ('payment', 'Payment'),
    )
    
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    related_account = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name='related_transactions')
    
    def __str__(self):
        return f"{self.transaction_type} of ${self.amount} for {self.account}"
    
class AccountHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    checking_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    savings_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    business_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    crypto_balance = models.DecimalField(max_digits=20, decimal_places=8, default=0)

    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'date']