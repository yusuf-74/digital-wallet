from django_filters import rest_framework as filters

from .models import Currency


class CurrencyFilter(filters.FilterSet):
    class Meta:
        model = Currency
        fields = {
            'currency_name': ['iexact', 'icontains'],
            'currency_code': ['iexact', 'icontains'],
            'is_active': ['exact'],
        }
