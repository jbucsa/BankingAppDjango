# crypto/admin.py
from django.contrib import admin

from .models import Cryptocurrency, CryptoAccount, CryptoTransaction

class CryptocurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'current_price', 'last_updated')
    search_fields = ('name', 'symbol')
    readonly_fields = ('last_updated',)

class CryptoAccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'user', 'balance')
    search_fields = ('account_number', 'user__username')

class CryptoTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'crypto', 'transaction_type', 'amount', 'status', 'timestamp')
    search_fields = ('user__username', 'crypto__symbol')
    list_filter = ('transaction_type', 'status', 'timestamp')

admin.site.register(Cryptocurrency, CryptocurrencyAdmin)
admin.site.register(CryptoAccount, CryptoAccountAdmin)
admin.site.register(CryptoTransaction, CryptoTransactionAdmin)