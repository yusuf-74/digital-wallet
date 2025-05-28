from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from utilities.models import Currency
from utils.data_generators import (
    generate_otp,
    generate_reference,
    generate_unique_wallet_name,
)


class Wallet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    name = models.CharField(max_length=100, blank=True, null=True, help_text=_('Optional name for the wallet'))
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    currency = models.ForeignKey(
        Currency, on_delete=models.PROTECT, related_name='wallets', help_text=_('Currency of the wallet')
    )
    transferred_today = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_('Amount that has been transferred today from this wallet'),
    )
    withdrawn_today = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_('Amount that has been withdrawn today from this wallet'),
    )
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Wallet')
        verbose_name_plural = _('Wallets')
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(check=models.Q(balance__gte=Decimal('0.00')), name='balance_non_negative'),
            models.UniqueConstraint(fields=['user', 'name'], name='unique_wallet_name_per_user'),
        ]
        indexes = [
            models.Index(fields=['user', 'currency']),
        ]

    def save(self, *args, **kwargs):
        if not self.name:
            existing_names = Wallet.objects.filter(user=self.user).values_list('name', flat=True)
            self.name = generate_unique_wallet_name(existing_names, self.currency.currency_code)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}'s ({self.user.phone_number}) Wallet - {self.currency.currency_code} {self.balance:.2f}"


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        DEPOSIT = 'DEPOSIT', _('Deposit')
        WITHDRAWAL = 'WITHDRAWAL', _('Withdrawal')
        TRANSFER_IN = 'TRANSFER_IN', _('Transfer In')
        TRANSFER_OUT = 'TRANSFER_OUT', _('Transfer Out')

    class MoneySource(models.TextChoices):
        BANK_TRANSFER = 'BANK_TRANSFER', _('Bank Transfer')
        ATM = 'ATM', _('ATM/Cash')
        WALLET_TO_WALLET = 'WALLET_TO_WALLET', _('Wallet to Wallet')

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PROCESSING = 'PROCESSING', _('Processing')
        DECLINED = 'DECLINED', _('Declined')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')
        EXPIRED = 'EXPIRED', _('Expired')
        CANCELED = 'CANCELED', _('Canceled')

    wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=12, choices=TransactionType.choices)
    money_source = models.CharField(max_length=20, choices=MoneySource.choices)
    reference = models.CharField(max_length=100)
    related_wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT, related_name='related_transactions', null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    description = models.TextField(null=True)
    extra_info = models.JSONField(null=True, blank=True, help_text=_('Additional information about the transaction'))
    expires_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')
        ordering = ['-id']
        constraints = [models.CheckConstraint(check=models.Q(amount__gt=Decimal('0.00')), name='amount_positive')]
        indexes = [
            models.Index(fields=['wallet', 'transaction_type', 'status']),
            models.Index(fields=['reference']),
        ]

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} {self.wallet.currency} on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

    def save(self, *args, **kwargs):
        if not self.reference and not self.pk:
            self.reference = generate_reference(prefix='TXN')
        if not self.expires_at and not self.pk:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at and self.status == self.Status.PENDING


class ATMCode(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='atm_codes',
        help_text=_('User associated with the ATM code'),
    )
    code = models.CharField(max_length=6, unique=True, help_text=_('Unique ATM code'))
    is_used = models.BooleanField(default=False, help_text=_('Indicates if the ATM code is active'))
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('ATM Code')
        verbose_name_plural = _('ATM Codes')
        ordering = ['-created_at']

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code and not self.pk:
            self.code = generate_otp()
        if not self.expires_at and not self.pk:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    def mark_as_used(self):
        if not self.is_used:
            self.is_used = True
            self.save(update_fields=['is_used'])
        else:
            raise ValueError("This ATM code has already been used.")


class Tier(models.Model):
    name = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True, help_text=_('Description of the tier and its benefits'))
    number_of_wallets = models.IntegerField(default=5, help_text=_('Number of wallets allowed for this tier'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tier"
        verbose_name_plural = "Tiers"
        ordering = ['-id']

    def __str__(self):
        return self.name


class TierCurrencyLimit(models.Model):
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE, related_name='currency_limits')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='tier_limits')
    daily_withdrawal_limit = models.DecimalField(max_digits=12, decimal_places=2)
    daily_transfer_limit = models.DecimalField(max_digits=12, decimal_places=2)
    daily_transactions_limit = models.IntegerField(
        help_text="Maximum number of transactions allowed per day for this tier and currency"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tier Currency Limit"
        verbose_name_plural = "Tier Currency Limits"
        ordering = ['tier__name', 'currency__currency_code']
        constraints = [
            models.UniqueConstraint(fields=['tier', 'currency'], name='unique_tier_currency_limit'),
            models.CheckConstraint(
                check=models.Q(daily_withdrawal_limit__gte=Decimal('0.00')), name='daily_withdrawal_limit_non_negative'
            ),
            models.CheckConstraint(
                check=models.Q(daily_transfer_limit__gte=Decimal('0.00')), name='daily_transfer_limit_non_negative'
            ),
            models.CheckConstraint(
                check=models.Q(daily_transactions_limit__gte=0), name='daily_transactions_limit_non_negative'
            ),
        ]

    def __str__(self):
        return f"{self.tier.name} - {self.currency.currency_code} Limits"
