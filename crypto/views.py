# crypto/views.py
import requests
from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum

from .models import Cryptocurrency, CryptoAccount, CryptoTransaction
from .forms import CryptoTransferForm, BuySellCryptoForm, CryptoWithdrawalForm
from banking.models import BankAccount, Transaction

def fetch_crypto_prices():
    # In a real app, you'd use an actual API like CoinGecko or CoinMarketCap
    # This is a simplified mock implementation
    cryptos = Cryptocurrency.objects.all()
    for crypto in cryptos:
        # Simulate price changes
        crypto.current_price = Decimal(crypto.current_price) * Decimal('1.01')
        crypto.save()
    return cryptos

@login_required
def crypto_home_view(request):
    try:
        crypto_account = CryptoAccount.objects.get(user=request.user)
    except CryptoAccount.DoesNotExist:
        crypto_account = CryptoAccount.objects.create(
            user=request.user,
            account_number=f"CRYPTO{request.user.id}{CryptoAccount.objects.count() + 1}"
        )
    
    cryptos = fetch_crypto_prices()
    transactions = CryptoTransaction.objects.filter(user=request.user).order_by('-timestamp')
    
    return render(request, 'crypto/crypto_home.html', {
        'crypto_account': crypto_account,
        'cryptos': cryptos,
        'transactions': transactions
    })


def transfer_to_crypto_view(request):
    crypto_account = CryptoAccount.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = CryptoTransferForm(request.user, request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            bank_account = form.cleaned_data['bank_account']
            
            if bank_account.balance >= Decimal(amount):
                bank_account.balance -= Decimal(amount)
                crypto_account.balance += Decimal(amount)
                bank_account.save()
                crypto_account.save()
                
                Transaction.objects.create(
                    account=bank_account,
                    transaction_type='transfer',
                    amount=amount,
                    description=f"Transfer to crypto account {crypto_account.account_number}"
                )
                
                messages.success(request, 'Transfer successful!')
                return redirect('crypto_home')
            else:
                messages.error(request, 'Insufficient funds')
    else:
        form = CryptoTransferForm(request.user)
    
    return render(request, 'crypto/transfer_to_crypto.html', {'form': form})

@login_required
def transfer_from_crypto_view(request):
    crypto_account = CryptoAccount.objects.get(user=request.user)
    bank_accounts = BankAccount.objects.filter(user=request.user)
    
    # Calculate available balance (total minus pending orders)
    pending_orders = CryptoTransaction.objects.filter(
        user=request.user,
        status='pending'
    ).aggregate(total_pending=Sum('total_value'))['total_pending'] or 0
    
    available_balance = crypto_account.balance - Decimal(pending_orders)
    
    if request.method == 'POST':
        form = CryptoWithdrawalForm(request.user, request.POST)
        if form.is_valid():
            amount = Decimal(form.cleaned_data['amount'])
            bank_account = form.cleaned_data['bank_account']
            
            if amount <= available_balance:
                crypto_account.balance -= amount
                bank_account.balance += amount
                crypto_account.save()
                bank_account.save()
                
                Transaction.objects.create(
                    account=bank_account,
                    transaction_type='deposit',
                    amount=amount,
                    description=f"Transfer from crypto account {crypto_account.account_number}"
                )
                
                messages.success(request, 'Transfer to bank account successful!')
                return redirect('crypto_home')
            else:
                messages.error(request, 
                    f'Insufficient available funds. You have ${available_balance} available '
                    f'(excluding ${pending_orders} in pending orders)')
    else:
        form = CryptoWithdrawalForm(request.user)
    
    return render(request, 'crypto/transfer_from_crypto.html', {
        'form': form,
        'available_balance': available_balance
    })

@login_required
def buy_crypto_view(request):
    cryptos = Cryptocurrency.objects.all()
    
    if request.method == 'POST':
        form = BuySellCryptoForm(request.POST)
        if form.is_valid():
            crypto = form.cleaned_data['crypto']
            amount = form.cleaned_data['amount']
            crypto_account = CryptoAccount.objects.get(user=request.user)
            
            total_cost = float(amount) * float(crypto.current_price)
            
            if crypto_account.balance >= Decimal(total_cost):
                # Reserve funds for the order
                crypto_account.balance -= Decimal(total_cost)
                crypto_account.save()
                
                CryptoTransaction.objects.create(
                    user=request.user,
                    crypto=crypto,
                    transaction_type='buy',
                    amount=amount,
                    price_at_transaction=crypto.current_price,
                    total_value=total_cost,
                    status='pending'
                )
                
                messages.success(request, f'Buy order for {amount} {crypto.symbol} submitted!')
                return redirect('crypto_home')
            else:
                messages.error(request, 'Insufficient funds in crypto account')
    else:
        form = BuySellCryptoForm()
    
    return render(request, 'crypto/buy_crypto.html', {
        'form': form,
        'cryptos': cryptos
    })

@login_required
def sell_crypto_view(request):
    cryptos = Cryptocurrency.objects.all()
    
    if request.method == 'POST':
        form = BuySellCryptoForm(request.POST)
        if form.is_valid():
            crypto = form.cleaned_data['crypto']
            amount = form.cleaned_data['amount']
            
            # Check available balance (would need a CryptoHolding model in real implementation)
            transaction = CryptoTransaction(
                user=request.user,
                crypto=crypto,
                transaction_type='sell',
                amount=amount,
                price_at_transaction=crypto.current_price,
                total_value=float(amount) * float(crypto.current_price),
                status='pending'
            )
            transaction.save()
            
            messages.success(request, f'Sell order for {amount} {crypto.symbol} submitted!')
            return redirect('crypto_home')
    else:
        form = BuySellCryptoForm()
    
    return render(request, 'crypto/sell_crypto.html', {
        'form': form,
        'cryptos': cryptos
    })

@login_required
def admin_approve_transactions(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    pending_transactions = CryptoTransaction.objects.filter(status='pending').order_by('timestamp')
    
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        action = request.POST.get('action')
        
        try:
            transaction = CryptoTransaction.objects.get(id=transaction_id)
            crypto_account = CryptoAccount.objects.get(user=transaction.user)
            
            if action == 'approve':
                if transaction.transaction_type == 'buy':
                    crypto_account.balance -= Decimal(transaction.total_value)
                    # In a real app, you'd also track the specific crypto holdings
                elif transaction.transaction_type == 'sell':
                    crypto_account.balance += Decimal(transaction.total_value)
                    # Deduct from crypto holdings in a real app
                
                crypto_account.save()
                transaction.status = 'completed'
                transaction.save()
                messages.success(request, f'Transaction {transaction_id} approved.')
            elif action == 'reject':
                transaction.status = 'rejected'
                transaction.save()
                messages.success(request, f'Transaction {transaction_id} rejected.')
        except CryptoTransaction.DoesNotExist:
            messages.error(request, 'Transaction not found.')
    
    return render(request, 'crypto/admin_approve.html', {'transactions': pending_transactions})