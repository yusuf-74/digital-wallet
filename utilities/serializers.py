from core.base.serializers import BaseModelSerializer

from .models import Currency, SystemMessage


class CurrencySerializer(BaseModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'


class SystemMessagesSerializer(BaseModelSerializer):
    class Meta:
        model = SystemMessage
        fields = '__all__'
