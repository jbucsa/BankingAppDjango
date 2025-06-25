from decimal import Decimal
from django.test import TestCase
from banking.models import BankAccount, Transaction

class TransactionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.account = BankAccount.objects.create(
            user=self.user,
            account_type='checking',
            account_number='TEST123',
            balance=Decimal('1000.00')
        )

    def test_deposit(self):
        initial_balance = self.account.balance
        self.client.force_login(self.user)
        response = self.client.post(reverse('deposit', args=[self.account.id]), {
            'amount': '500.00',
            'description': 'Test deposit'
        })
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, initial_balance + Decimal('500.00'))
        self.assertTrue(Transaction.objects.filter(amount=500).exists())

    def test_insufficient_withdrawal(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('withdraw', args=[self.account.id]), {
            'amount': '2000.00',
            'description': 'Test withdrawal'
        })
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal('1000.00'))  # Balance unchanged
        self.assertContains(response, "Insufficient funds")  # Check error message