from django_filters import rest_framework as filters

from .models import Transaction, Wallet


class WalletFilter(filters.FilterSet):
    phone_number = filters.CharFilter(field_name='user__phone_number', lookup_expr='icontains')

    class Meta:
        model = Wallet
        fields = {
            'user': ['exact'],
            'is_active': ['exact'],
            'currency': ['exact'],
        }


class TransactionFilter(filters.FilterSet):
    transaction_type = filters.ChoiceFilter(choices=Transaction.TransactionType.choices)
    status = filters.ChoiceFilter(choices=Transaction.Status.choices)
    money_source = filters.ChoiceFilter(choices=Transaction.MoneySource.choices)

    class Meta:
        model = Transaction
        fields = {
            'wallet': ['exact'],
            'related_wallet': ['exact'],
        }
