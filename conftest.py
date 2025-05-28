from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from authentication.models import User
from utilities.models import Currency
from wallets.models import Tier, TierCurrencyLimit, Wallet


# --- Client Fixtures ---
@pytest.fixture
def client():
    return APIClient()


# --- Currency Fixtures ---
@pytest.fixture
@pytest.mark.django_db
def usd_currency(admin_user):
    currency, _ = Currency.objects.get_or_create(
        currency_name="US Dollar", currency_code="USD", symbol="$", last_updated_by=admin_user
    )
    return currency


@pytest.fixture
@pytest.mark.django_db
def eur_currency(admin_user):
    currency, _ = Currency.objects.get_or_create(
        currency_name="Euro", currency_code="EUR", symbol="€", last_updated_by=admin_user
    )
    return currency


@pytest.fixture
@pytest.mark.django_db
def default_tier(usd_currency, eur_currency):
    tier, _ = Tier.objects.get_or_create(
        name="basic", defaults={"description": "Basic user tier", "number_of_wallets": 5}
    )

    TierCurrencyLimit.objects.get_or_create(
        tier=tier,
        currency=usd_currency,
        defaults={
            "daily_withdrawal_limit": Decimal("1000.00"),
            "daily_transfer_limit": Decimal("5000.00"),
            "daily_transactions_limit": 100,
        },
    )
    TierCurrencyLimit.objects.get_or_create(
        tier=tier,
        currency=eur_currency,
        defaults={
            "daily_withdrawal_limit": Decimal("800.00"),
            "daily_transfer_limit": Decimal("4000.00"),
            "daily_transactions_limit": 100,
        },
    )
    return tier


@pytest.fixture
@pytest.mark.django_db
def admin_user():
    user = User.objects.create_superuser(
        phone_number='+1234567890',
        password='654321',
        first_name='Admin',
        last_name='User',
        is_verified=True,
        date_of_birth='1990-01-01',
    )
    return user


@pytest.fixture
@pytest.mark.django_db
def test_user_a(default_tier):
    user = User.objects.create_user(
        phone_number='+1234567891',
        password='123456',
        first_name='Test',
        last_name='User A',
        is_verified=True,
        date_of_birth='1990-01-01',
    )
    user.tier = default_tier
    return user


@pytest.fixture
@pytest.mark.django_db
def test_user_b(default_tier):
    user = User.objects.create_user(
        phone_number='+1234567892',
        password='123456',
        first_name='Test',
        last_name='User B',
        is_verified=True,
        date_of_birth='1990-01-01',
    )
    user.tier = default_tier
    return user


@pytest.fixture
@pytest.mark.django_db
def test_unverified_user(default_tier):
    user = User.objects.create_user(
        phone_number='+1234567893',
        password='123456',
        first_name='Test',
        last_name='Unverified User',
        is_verified=False,
        date_of_birth='1990-01-01',
    )
    user.tier = default_tier
    return user


@pytest.fixture
@pytest.mark.django_db
def test_inactive_user(default_tier):
    user = User.objects.create_user(
        phone_number='+1234567894',
        password='123456',
        first_name='Test',
        last_name='Inactive User',
        is_verified=True,
        date_of_birth='1990-01-01',
    )
    user.is_active = False
    user.tier = default_tier
    user.save()
    return user


@pytest.fixture
def admin_client(client, admin_user):
    client.force_authenticate(user=admin_user)
    return client


@pytest.fixture
def user_a_client(client, test_user_a):
    client.force_authenticate(user=test_user_a)
    return client


@pytest.fixture
def user_b_client(client, test_user_b):
    client.force_authenticate(user=test_user_b)
    return client


@pytest.fixture
def unverified_user_client(client, test_unverified_user):
    client.force_authenticate(user=test_unverified_user)
    return client


@pytest.fixture
def inactive_user_client(client, test_inactive_user):
    client.force_authenticate(user=test_inactive_user)
    return client


@pytest.fixture
@pytest.mark.django_db
def user_a_primary_usd_wallet(test_user_a, usd_currency):
    return Wallet.objects.create(
        user=test_user_a, name="User A Primary USD", currency=usd_currency, balance=Decimal("500.00")
    )


@pytest.fixture
@pytest.mark.django_db
def user_a_secondary_usd_wallet(test_user_a, usd_currency):
    return Wallet.objects.create(
        user=test_user_a, name="User A Secondary USD", currency=usd_currency, balance=Decimal("500.00")
    )


@pytest.fixture
@pytest.mark.django_db
def user_a_eur_wallet(test_user_a, eur_currency):
    return Wallet.objects.create(
        user=test_user_a, name="User A EUR Savings", currency=eur_currency, balance=Decimal("300.00")
    )


@pytest.fixture
@pytest.mark.django_db
def user_b_primary_usd_wallet(test_user_b, usd_currency, default_tier):
    return Wallet.objects.create(
        user=test_user_b, name="User B Primary USD", currency=usd_currency, balance=Decimal("700.00")
    )


@pytest.fixture
@pytest.mark.django_db
def user_b_secondary_usd_wallet(test_user_b, usd_currency, default_tier):
    return Wallet.objects.create(
        user=test_user_b, name="User B Secondary USD", currency=usd_currency, balance=Decimal("700.00")
    )


@pytest.fixture
@pytest.mark.django_db
def user_b_eur_wallet(test_user_b, eur_currency):
    return Wallet.objects.create(
        user=test_user_b, name="User B Main EUR", currency=eur_currency, balance=Decimal("700.00")
    )
