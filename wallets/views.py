from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import User
from core.base.views import (
    UnifiedResponseListAPIView,
    UnifiedResponseListCreateAPIView,
    UnifiedResponseRetrieveUpdateDestroyAPIView,
)
from utils.orm_utils import query_optimizer

from .events import EventsHandler
from .filters import TransactionFilter, WalletFilter
from .models import ATMCode, Transaction, Wallet
from .serializers import (
    TransactionSerializer,
    WalletSerializer,
    WalletTransferSerializer,
)
from .utils import NotificationOperator, TransactionOperator, verify_webhook_signature


class WalletListCreateView(UnifiedResponseListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filterset_class = WalletFilter
    search_fields = ['name', 'user__phone_number']
    ordering_fields = ['created_at', 'balance']
    serializer_class = WalletSerializer

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return query_optimizer(Wallet, self.request)
        return query_optimizer(Wallet, self.request).filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if not request.user.is_staff:
            data['user'] = request.user.id

        try:
            user_tier = User.objects.filter(id=data['user']).first().tier
        except:
            return Response(
                {
                    'success': False,
                    'message': _("User tier not found. Please ensure the user has a valid tier."),
                    'data': None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user_tier.number_of_wallets <= Wallet.objects.filter(user=data['user']).count():
            return Response(
                {
                    'success': False,
                    'message': _("User has reached the maximum number of wallets allowed for their tier."),
                    'data': None,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = WalletSerializer(data=data, context={'request': request})
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': _("Invalid data provided."), 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return Response(
            {'success': True, 'message': _("Wallet has been successfully created."), 'data': serializer.data},
            status=status.HTTP_201_CREATED,
        )


class WalletRetrieveUpdateDestroyView(UnifiedResponseRetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WalletSerializer

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return query_optimizer(Wallet, self.request)
        return query_optimizer(Wallet, self.request).filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_active:
            instance.is_active = False
            instance.save()
            return Response(
                {'success': True, 'message': _("Wallet has been successfully deactivated."), 'data': None},
                status=status.HTTP_204_NO_CONTENT,
            )
        else:
            return Response(
                {'success': False, 'message': _("Wallet is already inactive and cannot be deleted."), 'data': None},
                status=status.HTTP_400_BAD_REQUEST,
            )


class TransactionListView(UnifiedResponseListAPIView):
    permission_classes = [IsAuthenticated]
    filterset_class = TransactionFilter
    serializer_class = TransactionSerializer
    search_fields = ['reference', 'wallet__user__phone_number', 'related_wallet__user__phone_number']
    ordering_fields = ['created_at', 'amount']

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return query_optimizer(Transaction, self.request)
        return query_optimizer(Transaction, self.request).filter(wallet__user=self.request.user)


class RequestATMCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        atm_code = ATMCode.objects.create(user=user)
        atm_code.save()

        NotificationOperator.send_atm_code(user.phone_number, atm_code.code)
        return Response(
            {
                'success': True,
                'message': _("ATM code has been successfully created and sent to your phone."),
            },
            status=status.HTTP_201_CREATED,
        )


class TransferMoneyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        source_wallet = request.data.get('source_wallet')
        target_wallet = request.data.get('target_wallet')
        amount = request.data.get('amount')
        description = request.data.get('description', '')

        serializer = WalletTransferSerializer(
            data={
                'source_wallet': source_wallet,
                'target_wallet': target_wallet,
                'amount': amount,
                'description': description,
            },
            context={'request': request},
        )

        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': _("Invalid data provided."), 'errors': serializer._errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reference = TransactionOperator.initiate_wallet_to_wallet_transfer(
            source=serializer.validated_data['source_wallet'],
            target=serializer.validated_data['target_wallet'],
            amount=serializer.validated_data['amount'],
            description=serializer.validated_data['description'],
        )

        NotificationOperator.send_transfer_notification(
            source=serializer.validated_data['source_wallet'],
            target=serializer.validated_data['target_wallet'],
            amount=serializer.validated_data['amount'],
            reference=reference,
        )

        return Response(
            {
                'success': True,
                'message': _("Transfer initiated successfully."),
                'data': {
                    'source_wallet': source_wallet,
                    'target_wallet': target_wallet,
                    'amount': amount,
                    'description': description,
                    'reference': reference,
                },
            },
            status=status.HTTP_200_OK,
        )


class TransferActionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        reference = request.data.get('reference')
        action = request.data.get('action')

        if not reference:
            return Response(
                {'success': False, 'message': _("Reference is required to accept the transfer."), 'data': None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            TransactionOperator.finalize_transfer(reference, action)
            return Response(
                {
                    'success': True,
                    'message': _(
                        f"Transfer has been successfully {'Processed' if action == 'accept' else 'Declined'}."
                    ),
                    'data': None,
                },
                status=status.HTTP_200_OK,
            )
        except ValueError as e:
            return Response({'success': False, 'message': str(e), 'data': None}, status=status.HTTP_400_BAD_REQUEST)


class CancelTransferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        reference = request.data.get('reference')

        if not reference:
            return Response(
                {'success': False, 'message': _("Reference is required to cancel the transfer."), 'data': None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            TransactionOperator.cancel_transfer(reference)
            return Response(
                {'success': True, 'message': _("Transfer has been successfully canceled."), 'data': None},
                status=status.HTTP_200_OK,
            )
        except ValueError as e:
            return Response({'success': False, 'message': str(e), 'data': None}, status=status.HTTP_400_BAD_REQUEST)


class BankWebhook(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        event = request.data
        if not verify_webhook_signature(request):
            return Response({"success": False, "message": _("Invalid signature.")}, status=status.HTTP_403_FORBIDDEN)

        events_handler = EventsHandler()
        response = events_handler.handle_event(event)

        return Response(response, status=(status.HTTP_200_OK if response['success'] else status.HTTP_400_BAD_REQUEST))
