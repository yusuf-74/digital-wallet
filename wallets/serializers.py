from decimal import Decimal

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from core.base.serializers import BaseModelSerializer, BaseSerializer
from utilities.serializers import CurrencySerializer

from .models import Tier, TierCurrencyLimit, Transaction, Wallet


class WalletSerializer(BaseModelSerializer):
    class Meta:
        model = Wallet
        fields = '__all__'
        read_only_fields = ('id', 'balance', 'created_at', 'updated_at', 'transferred_today', 'withdrawn_today')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        expand = self.context.get('request').query_params.get('expand', '')
        if 'currency' in expand:
            representation['currency'] = CurrencySerializer(
                instance.currency, context={'request': self.context.get('request')}
            ).data
        if 'transactions' in expand:
            representation['transactions'] = TransactionSerializer(
                instance.transactions.all(), many=True, context={'request': self.context.get('request')}
            ).data
        if 'user' in expand:
            representation['user'] = {
                'id': instance.user.id,
                'full_name': f"{instance.user.first_name} {instance.user.last_name}",
                'phone_number': instance.user.phone_number,
            }
        if 'user.tier' in expand:
            representation['user']['tier'] = {
                'id': instance.user.tier.id,
                'name': instance.user.tier.name,
            }
        return representation


class TransactionSerializer(BaseModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ('id', 'status', 'created_at', 'updated_at')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        expand = self.context.get('request').query_params.get('expand', '')
        if 'wallet' in expand:
            representation['wallet'] = WalletSerializer(instance.wallet, context=self.context).data
        if 'related_wallet' in expand:
            representation['related_wallet'] = WalletSerializer(instance.related_wallet, context=self.context).data
        return representation

    def validate(self, attrs):
        if attrs['amount'] <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return attrs


class TierSerializer(BaseModelSerializer):
    class Meta:
        model = Tier
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class TierCurrencyLimitSerializer(BaseModelSerializer):
    tier = TierSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)

    class Meta:
        model = TierCurrencyLimit
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class WalletTransferSerializer(BaseSerializer):
    source_wallet = serializers.IntegerField()
    target_wallet = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    description = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate(self, attrs):
        source_wallet_id = attrs.get('source_wallet')
        target_wallet_id = attrs.get('target_wallet')
        amount = attrs.get('amount')
        source_wallet = Wallet.objects.filter(id=source_wallet_id, user=self.context['request'].user).first()
        target_wallet = Wallet.objects.filter(id=target_wallet_id).first()

        if not source_wallet or not target_wallet:
            raise serializers.ValidationError(_("Invalid source or target wallet."))

        if not source_wallet.is_active or not target_wallet.is_active:
            raise serializers.ValidationError(_("Both wallets must be active to perform a transfer."))

        if source_wallet.currency != target_wallet.currency:
            raise serializers.ValidationError(_("Source and target wallets must have the same currency."))

        if source_wallet.id == target_wallet.id:
            raise serializers.ValidationError(_("Cannot transfer to the same wallet."))
        try:
            amount = Decimal(amount)
            if amount <= 0:
                raise serializers.ValidationError(_("Amount must be greater than zero."))
        except (ValueError, TypeError):
            raise serializers.ValidationError(_("Invalid amount format."))
        if source_wallet.balance < amount:
            raise serializers.ValidationError(_("Source wallet does not have sufficient balance."))

        attrs['source_wallet'] = source_wallet
        attrs['target_wallet'] = target_wallet

        return super().validate(attrs)


class ATMDepositSerializer(BaseSerializer):
    target_wallet = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate(self, attrs):
        target_wallet = Wallet.objects.filter(id=attrs.get('target_wallet')).first()
        if not target_wallet:
            raise serializers.ValidationError(_("Invalid target wallet."))

        if not target_wallet.is_active:
            raise serializers.ValidationError(_("Wallet must be active to perform a transfer."))

        attrs['target_wallet'] = target_wallet
        return super().validate(attrs)


class ATMWithdrawalSerializer(BaseSerializer):
    source_wallet = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)

    def validate(self, attrs):
        source_wallet = Wallet.objects.filter(id=attrs.get('source_wallet')).first()
        if not source_wallet:
            raise serializers.ValidationError(_("Invalid target wallet."))

        if not source_wallet.is_active:
            raise serializers.ValidationError(_("Wallet must be active to perform a transfer."))

        if source_wallet.balance < Decimal(attrs.get('amount')):
            raise serializers.ValidationError(_("Source wallet does not have sufficient balance."))

        attrs['source_wallet'] = source_wallet

        return super().validate(attrs)
