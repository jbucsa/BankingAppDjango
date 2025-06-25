from decimal import Decimal
from django.test import TestCase
from banking.models import BankAccount
from crypto.models import CryptoAccount, Cryptocurrency

class CryptoTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.bank_account = BankAccount.objects.create(
            user=self.user,
            account_type='checking',
            balance=Decimal('1000.00')
        )
        self.crypto_account = CryptoAccount.objects.create(user=self.user, balance=Decimal('0.00'))
        self.btc = Cryptocurrency.objects.create(
            name='Bitcoin',
            symbol='BTC',
            current_price=Decimal('50000.00')
        )

    def test_transfer_to_crypto(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('transfer_to_crypto'), {
            'amount': '500.00',
            'bank_account': self.bank_account.id
        })
        self.bank_account.refresh_from_db()
        self.crypto_account.refresh_from_db()
        self.assertEqual(self.bank_account.balance, Decimal('500.00'))
        self.assertEqual(self.crypto_account.balance, Decimal('500.00'))