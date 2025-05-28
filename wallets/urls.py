from django.urls import path

from .views import (
    BankWebhook,
    CancelTransferView,
    RequestATMCodeView,
    TransactionListView,
    TransferActionView,
    TransferMoneyView,
    WalletListCreateView,
    WalletRetrieveUpdateDestroyView,
)

urlpatterns = [
    path('', WalletListCreateView.as_view(), name='wallet-list-create'),
    path('<int:pk>/', WalletRetrieveUpdateDestroyView.as_view(), name='wallet-detail'),
    path('bank-webhook/', BankWebhook.as_view(), name='bank-webhook'),
    path('transfer-money/', TransferMoneyView.as_view(), name='transfer-money'),
    path('transfer-action/', TransferActionView.as_view(), name='transfer-action'),
    path('cancel-transfer/', CancelTransferView.as_view(), name='cancel-transfer'),
    path('request-atm-code/', RequestATMCodeView.as_view(), name='request-atm-code'),
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
]
