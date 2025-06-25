# banking/forms.py
from django import forms

from .models import BankAccount, Transaction

class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ['account_type']

class DepositWithdrawalForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'description']
        widgets = {
            'amount': forms.NumberInput(attrs={'min': 0.01}),
        }

class TransferForm(forms.ModelForm):
    to_account = forms.CharField(max_length=20, label="To Account Number")
    
    class Meta:
        model = Transaction
        fields = ['amount', 'description']
        widgets = {
            'amount': forms.NumberInput(attrs={'min': 0.01}),
        }