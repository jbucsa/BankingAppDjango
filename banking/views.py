# banking/views.py
from datetime import datetime, timedelta
import json

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum

from banking.models import BankAccount, Transaction, AccountHistory
from crypto.models import CryptoAccount, CryptoTransaction
from .models import BankAccount, Transaction
from .forms import BankAccountForm, DepositWithdrawalForm, TransferForm
from decimal import Decimal



def get_account_color(account_type):
    colors = {
        'checking': '#36A2EB',
        'savings': '#4BC0C0',
        'business': '#FFCE56'
    }
    return colors.get(account_type, '#9966FF')

def generate_mock_history(current_balance, time_delta, volatility=1.0):
    """Generate realistic mock historical data"""
    import random
    base_value = float(current_balance)
    return [
        round(base_value * (1 + (random.random() - 0.5) * volatility * 0.1 * (i+1)), 2)
        for i in range(7)
    ]

def interpolate_history(history, interval):
    """Create higher resolution data from daily snapshots"""
    from django.db.models.functions import Trunc
    from django.db.models import DateTimeField
    
    # This would need actual implementation based on your data
    # For now returns the raw history
    return history

def get_historical_data(user, time_range):
    now = timezone.now()
    
    if time_range == '1h':
        start_date = now - timedelta(hours=1)
        time_format = '%H:%M'
        interval = '5 minutes'
    elif time_range == '1d':
        start_date = now - timedelta(days=1)
        time_format = '%H:%M'
        interval = '1 hour'
    elif time_range == '1m':
        start_date = now - timedelta(days=30)
        time_format = '%m-%d'
        interval = '1 day'
    else:  # 7 days
        start_date = now - timedelta(days=7)
        time_format = '%m-%d'
        interval = '1 day'

    history = AccountHistory.objects.filter(
        user=user,
        date__gte=start_date
    ).order_by('date')

    # For higher resolution than daily snapshots
    if time_range == '1h' or time_range == '1d':
        history = interpolate_history(history, interval)

    return history, time_format


def generate_pie_data(accounts, crypto_account):
    pie_data = {
        'labels': [],
        'datasets': [{
            'data': [],
            'backgroundColor': []
        }]
    }

    # Add bank accounts
    for account in accounts:
        pie_data['labels'].append(account.get_account_type_display())
        pie_data['datasets'][0]['data'].append(float(account.balance))
        pie_data['datasets'][0]['backgroundColor'].append(
            get_account_color(account.account_type)
        )

    # Add crypto if exists
    if crypto_account:
        pie_data['labels'].append('Crypto Investments')
        pie_data['datasets'][0]['data'].append(float(crypto_account.balance))
        pie_data['datasets'][0]['backgroundColor'].append('#FF6384')

        # Add pending crypto transactions
        pending_total = CryptoTransaction.objects.filter(
            user=crypto_account.user,
            status='pending'
        ).aggregate(total=Sum('total_value'))['total'] or 0

        if pending_total > 0:
            pie_data['labels'].append('Pending Crypto Orders')
            pie_data['datasets'][0]['data'].append(float(pending_total))
            pie_data['datasets'][0]['backgroundColor'].append('#CCCCCC')

def create_daily_snapshot(user):
    """Create daily snapshot of all account balances"""
    accounts = BankAccount.objects.filter(user=user)
    checking = accounts.filter(account_type='checking').first()
    savings = accounts.filter(account_type='savings').first()
    business = accounts.filter(account_type='business').first()
    
    try:
        crypto_account = CryptoAccount.objects.get(user=user)
        crypto_balance = crypto_account.balance
    except CryptoAccount.DoesNotExist:
        crypto_balance = 0

    AccountHistory.objects.create(
        user=user,
        checking_balance=checking.balance if checking else 0,
        savings_balance=savings.balance if savings else 0,
        business_balance=business.balance if business else 0,
        crypto_balance=crypto_balance
    )


@login_required
def home_view(request):
    # Get all account data
    accounts = BankAccount.objects.filter(user=request.user)
    try:
        crypto_account = CryptoAccount.objects.get(user=request.user)
    except CryptoAccount.DoesNotExist:
        crypto_account = None
    
    # Calculate current totals
    current_data = {
        'checking': accounts.filter(account_type='checking').aggregate(Sum('balance'))['balance__sum'] or 0,
        'savings': accounts.filter(account_type='savings').aggregate(Sum('balance'))['balance__sum'] or 0,
        'business': accounts.filter(account_type='business').aggregate(Sum('balance'))['balance__sum'] or 0,
        'crypto': crypto_account.balance
    }


    # Calculate total balance
    total_balance = sum(account.balance for account in accounts)
    if crypto_account:
        total_balance += crypto_account.balance
    
    # Time range handling
    time_range = request.GET.get('range', '7d')  # Default 7 days
    now = datetime.now()
    
    if time_range == '1h':
        delta = timedelta(hours=1)
        time_format = '%H:%M'
    elif time_range == '1d':
        delta = timedelta(days=1)
        time_format = '%H:%M'
    elif time_range == '1m':
        delta = timedelta(days=30)
        time_format = '%m-%d'
    else:  # 7 days
        delta = timedelta(days=7)
        time_format = '%m-%d'

   # Get real historical data
    history, time_format = get_historical_data(request.user, time_range)
    
    # Generate time series data (show current values if no history)
    time_series = {
        'labels': ['Now'],
        'datasets': [
            {
                'label': 'Checking',
                'data': [float(current_data['checking'])],
                'borderColor': '#36A2EB'
            },
            {
                'label': 'Savings',
                'data': [float(current_data['savings'])],
                'borderColor': '#4BC0C0'
            },
            {
                'label': 'Business',
                'data': [float(current_data['business'])],
                'borderColor': '#FFCE56'
            },
            {
                'label': 'Crypto',
                'data': [float(current_data['crypto'])],
                'borderColor': '#FF6384'
            }
        ]
    }

    # Add checking account data
    if any(h.checking_balance for h in history):
        time_series['datasets'].append({
            'label': 'Checking Account',
            'data': [float(h.checking_balance) for h in history],
            'borderColor': '#36A2EB',
            'borderWidth': 2,
            'fill': False
        })

    # Add savings account data
    if any(h.savings_balance for h in history):
        time_series['datasets'].append({
            'label': 'Savings Account',
            'data': [float(h.savings_balance) for h in history],
            'borderColor': '#4BC0C0',
            'borderWidth': 2,
            'fill': False
        })

    # Add business account data
    if any(h.business_balance for h in history):
        time_series['datasets'].append({
            'label': 'Business Account',
            'data': [float(h.business_balance) for h in history],
            'borderColor': '#FFCE56',
            'borderWidth': 2,
            'fill': False
        })

    # Add crypto data
    if any(h.crypto_balance for h in history):
        time_series['datasets'].append({
            'label': 'Crypto Investments',
            'data': [float(h.crypto_balance) for h in history],
            'borderColor': '#FF6384',
            'borderWidth': 2,
            'fill': False
        })
    
    # Generate time labels
    time_series['labels'] = [
        (now - delta * (6-i)/6).strftime(time_format) 
        for i in range(7)
    ]

    # Generate pie chart data
    pie_data = {
        'labels': ['Checking', 'Savings', 'Business', 'Crypto'],
        'datasets': [{
            'data': [
                float(current_data['checking']),
                float(current_data['savings']),
                float(current_data['business']),
                float(current_data['crypto'])
            ],
            'backgroundColor': [
                '#36A2EB',
                '#4BC0C0',
                '#FFCE56',
                '#FF6384'
            ]
        }]
    }

    context = {
        'time_series': json.dumps(time_series),
        'pie_data': json.dumps(pie_data),
        'accounts': accounts,
        'total_balance': sum(current_data.values())
    }
    return render(request, 'banking/home.html', context)

@login_required
def create_account_view(request):
    if request.method == 'POST':
        form = BankAccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.account_number = f"{request.user.id}{BankAccount.objects.count() + 1}"
            account.save()
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = BankAccountForm()
    return render(request, 'banking/create_account.html', {'form': form})

@login_required
def deposit_view(request, account_id):
    account = BankAccount.objects.get(id=account_id, user=request.user)
    if request.method == 'POST':
        form = DepositWithdrawalForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            account.balance += Decimal(amount)
            account.save()
            Transaction.objects.create(
                account=account,
                transaction_type='deposit',
                amount=amount,
                description=form.cleaned_data['description']
            )
            messages.success(request, 'Deposit successful!')
            return redirect('home')
    else:
        form = DepositWithdrawalForm()
    return render(request, 'banking/deposit.html', {'form': form, 'account': account})

@login_required
def withdraw_view(request, account_id):
    account = BankAccount.objects.get(id=account_id, user=request.user)
    if request.method == 'POST':
        form = DepositWithdrawalForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            if account.balance >= Decimal(amount):
                account.balance -= Decimal(amount)
                account.save()
                Transaction.objects.create(
                    account=account,
                    transaction_type='withdrawal',
                    amount=amount,
                    description=form.cleaned_data['description']
                )
                messages.success(request, 'Withdrawal successful!')
                return redirect('home')
            else:
                messages.error(request, 'Insufficient funds.')
    else:
        form = DepositWithdrawalForm()
    return render(request, 'banking/withdraw.html', {'form': form, 'account': account})

@login_required
def transfer_view(request, account_id):
    from_account = BankAccount.objects.get(id=account_id, user=request.user)
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            to_account_number = form.cleaned_data['to_account']
            
            try:
                to_account = BankAccount.objects.get(account_number=to_account_number)
            except BankAccount.DoesNotExist:
                messages.error(request, 'Destination account not found.')
                return render(request, 'banking/transfer.html', {'form': form, 'account': from_account})
            
            if from_account.balance >= Decimal(amount):
                from_account.balance -= Decimal(amount)
                to_account.balance += Decimal(amount)
                from_account.save()
                to_account.save()
                
                Transaction.objects.create(
                    account=from_account,
                    transaction_type='transfer',
                    amount=amount,
                    description=form.cleaned_data['description'],
                    related_account=to_account
                )
                
                Transaction.objects.create(
                    account=to_account,
                    transaction_type='transfer',
                    amount=amount,
                    description=f"Incoming transfer from {from_account.user.username}",
                    related_account=from_account
                )
                
                messages.success(request, 'Transfer successful!')
                return redirect('home')
            else:
                messages.error(request, 'Insufficient funds.')
    else:
        form = TransferForm()
    return render(request, 'banking/transfer.html', {'form': form, 'account': from_account})

@login_required
def transaction_history_view(request):
    accounts = BankAccount.objects.filter(user=request.user)
    transactions = Transaction.objects.filter(account__in=accounts).order_by('-timestamp')
    return render(request, 'banking/transaction_history.html', {'transactions': transactions})