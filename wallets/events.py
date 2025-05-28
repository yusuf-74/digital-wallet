from abc import ABC, abstractmethod
from typing import Dict

from django.utils import timezone

from .models import ATMCode
from .serializers import ATMDepositSerializer, ATMWithdrawalSerializer
from .utils import NotificationOperator, TransactionOperator


class IBankEventHandler(ABC):
    @abstractmethod
    def handle_event(self, event):
        pass


class ATMDepositEventHandler(IBankEventHandler):
    def handle_event(self, event):
        serializer = ATMDepositSerializer(data={"target_wallet": event.get("wallet_id"), "amount": event.get("amount")})

        if not serializer.is_valid():
            return {'success': False, 'message': 'Validation error', 'errors': serializer._errors}
        try:
            transaction = TransactionOperator.atm_deposit(
                target=serializer.validated_data['target_wallet'], amount=serializer.validated_data['amount']
            )
            NotificationOperator.send_deposit_notification(transaction)
            return {
                'success': True,
                'message': 'Money recieved successfully',
            }
        except:
            return {'success': False, 'message': 'Unexpected error occured'}


class ATMWithdrawalEventHandler(IBankEventHandler):
    def handle_event(self, event):
        serializer = ATMWithdrawalSerializer(
            data={"source_wallet": event.get("wallet_id"), "amount": event.get("amount")}
        )

        if not serializer.is_valid():
            return {'success': False, 'message': 'Validation error', 'errors': serializer._errors}
        try:
            transaction = TransactionOperator.atm_withdrawal(
                source=serializer.validated_data['source_wallet'], amount=serializer.validated_data['amount']
            )
            NotificationOperator.send_withdrawal_notification(transaction)
            return {
                'success': True,
                'message': 'Money recieved successfully',
            }
        except ValueError as ve:
            return {'success': False, 'message': str(ve)}
        except Exception as e:
            print(f"Unexpected error: {e}", flush=True)
            return {'success': False, 'message': 'Unexpected error occured'}


class ATMLoginEventHandler(IBankEventHandler):
    def handle_event(self, event):
        phone_number = event.get("phone_number")
        pass_code = event.get("pass_code")

        if ATMCode.objects.filter(
            user__phone_number=phone_number, code=pass_code, is_used=False, expires_at__gt=timezone.now()
        ).exists():
            ATMCode.objects.filter(user__phone_number=phone_number, code=pass_code).first().mark_as_used()
            return {'success': True, 'message': 'Correct Credintials'}
        return {'success': False, 'message': 'Invalid ATM Code'}


class EventsHandler:
    def __init__(self):
        self._handlers: Dict[str, IBankEventHandler] = {
            'deposit': ATMDepositEventHandler(),
            'withdrawal': ATMWithdrawalEventHandler(),
            'login': ATMLoginEventHandler(),
        }

    def handle_event(self, event):
        event_type = event['type']
        if event_type in self._handlers:
            return self._handlers[event_type].handle_event(event)
        return {'success': False, 'message': 'Invalid Event type'}
