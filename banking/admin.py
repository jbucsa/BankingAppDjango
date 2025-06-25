# banking/admin.py
from django.contrib import admin

from .models import BankAccount, Transaction

class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'user', 'account_type', 'balance')
    search_fields = ('account_number', 'user__username')
    list_filter = ('account_type',)

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('account', 'transaction_type', 'amount', 'timestamp')
    search_fields = ('account__account_number', 'description')
    list_filter = ('transaction_type', 'timestamp')

admin.site.register(BankAccount, BankAccountAdmin)
admin.site.register(Transaction, TransactionAdmin)