# crypto/forms.py
from django import forms

from .models import CryptoTransaction, Cryptocurrency
from banking.models import BankAccount

class CryptoTransferForm(forms.Form):
    amount = forms.DecimalField(max_digits=20, decimal_places=8, min_value=0.00001)
    bank_account = forms.ModelChoiceField(queryset=BankAccount.objects.none())
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bank_account'].queryset = BankAccount.objects.filter(user=user)

class CryptoWithdrawalForm(forms.Form):
    amount = forms.DecimalField(max_digits=20, decimal_places=2, min_value=0.01)
    bank_account = forms.ModelChoiceField(queryset=BankAccount.objects.none())
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bank_account'].queryset = BankAccount.objects.filter(user=user)


class BuySellCryptoForm(forms.ModelForm):

    class Meta:
        model = CryptoTransaction
        fields = ['crypto', 'amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'min': 0.00001}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['crypto'].queryset = Cryptocurrency.objects.all()