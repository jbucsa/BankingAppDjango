
# Django Banking Application with Crypto Trading

![Banking App Screenshot](screenshot.png) Add actual screenshot later

A full-featured banking application with cryptocurrency trading capabilities, built with Django.

# Key Features

## Banking Features
- 🏦 Multi-account support (Checking, Savings, Business)
- 💸 Deposit/withdrawal functionality
- 🔄 Internal transfers between accounts
- 📊 Transaction history tracking
- 📈 Portfolio value tracking

## Crypto Features
- ₿ Crypto wallet integration
- 📉 Buy/sell cryptocurrencies
- 💱 Crypto-bank fund transfers
- ⏳ Pending order management
- 📉 Real-time price display (simulated)

## User Management
- 🔐 Email/password authentication
- 📝 User registration
- 👤 Profile management
- 🔒 Role-based access control

## Technology Stack

- **Backend**: Django 5.2
- **Frontend**: Bootstrap 5, Chart.js
- **Database**: SQLite (default), compatible with PostgreSQL
- **Authentication**: Django Allauth
- **Forms**: Django Crispy Forms

# Installation Guide

## Prerequisites
- Python 3.10+
- pip
- Virtualenv (recommended)

## Setup Instructions

1. Clone the repository
```bash
git clone https://github.com/yourusername/banking-app.git
cd banking-app
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
- Create ```.env``` file:
```bash
cp .env.example .env
```
- Edit ```.env``` with your settings:
```bash
SECRET_KEY=your-secret-key-here
DEBUG=True
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser
```bash
python manage.py createsuperuser
```

7. Load initial data (optional):
```bash
python manage.py loaddata initial_data.json
```

8. Run development server:
```bash
python manage.py runserver
```

9. Access the application:
- Open ```http://localhost:8000``` in your browser
- Admin panel: ```http://localhost:8000/admin```


# First-Time Setup
1. Create your first account:
- Log in with your superuser credentials
- Navigate to "Create Account" to set up your first bank account

2. Set up crypto wallet:
- Visit the Crypto page to initialize your wallet
- Add funds from your bank account

3. Configure admin approvals:
-As admin, visit ```/crypto/admin``` to approve pending transactions

# Application Structure

```bash
banking_project/
├── accounts/          # User authentication and profiles
├── banking/           # Core banking functionality
├── crypto/            # Cryptocurrency trading
├── static/            # CSS, JS, images
├── templates/         # HTML templates
├── manage.py          # Django management script
└── banking_project/   # Project configuration
```

# Test 
Run the test suite with:
```bash
python manage.py test
```
## Key test coverage:

- User authentication
- Transaction processing
- Balance calculations
- Form validations
- Template rendering

# Deployment

For production deployment:

1. Set DEBUG=False in .env
2. Configure a production database (PostgreSQL recommended)
3. Set up a proper web server (Nginx + Gunicorn)
4. Configure HTTPS


## Superuser : Admin
```bash
python manage.py createsuperuser

Admin:
Username: admin
Email: admin@bankingproject.com
password: 12345
```

## Test User

```bash
Username: TestTest
Email: Test@gmail.com
password: 12345lgp!@#
```