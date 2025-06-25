"""
URL configuration for banking_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

Created by: Justin Bucsa
"""
# banking_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from accounts import views as account_views
from banking import views as banking_views
from crypto import views as crypto_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', account_views.register_view, name='register'),
    path('login/', account_views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', account_views.profile_view, name='profile'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    
    # Banking URLs
    path('', banking_views.home_view, name='home'),
    path('create-account/', banking_views.create_account_view, name='create_account'),
    path('deposit/<int:account_id>/', banking_views.deposit_view, name='deposit'),
    path('withdraw/<int:account_id>/', banking_views.withdraw_view, name='withdraw'),
    path('transfer/<int:account_id>/', banking_views.transfer_view, name='transfer'),
    path('transactions/', banking_views.transaction_history_view, name='transaction_history'),
    
    # Crypto URLs
    path('crypto/', crypto_views.crypto_home_view, name='crypto_home'),

    path('crypto/transfer/', crypto_views.transfer_to_crypto_view, name='transfer_to_crypto'),
    path('crypto/transfer-from/', crypto_views.transfer_from_crypto_view, name='transfer_from_crypto'),



    path('crypto/transfer-to-bank/', crypto_views.transfer_from_crypto_view, name='transfer_from_crypto'),
    path('crypto/buy/', crypto_views.buy_crypto_view, name='buy_crypto'),
    path('crypto/sell/', crypto_views.sell_crypto_view, name='sell_crypto'),
    path('crypto/admin/', crypto_views.admin_approve_transactions, name='admin_approve'),
]