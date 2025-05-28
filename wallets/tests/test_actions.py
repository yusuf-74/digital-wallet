from decimal import Decimal
from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status

from wallets.models import ATMCode, TierCurrencyLimit, Transaction

WALLET_LIST_CREATE_URL = reverse('wallet-list-create')
TRANSACTION_LIST_URL = reverse('transaction-list')
REQUEST_ATM_CODE_URL = reverse('request-atm-code')
TRANSFER_MONEY_URL = reverse('transfer-money')
TRANSFER_ACTION_URL = reverse('transfer-action')
CANCEL_TRANSFER_URL = reverse('cancel-transfer')
BANK_WEBHOOK_URL = reverse('bank-webhook')


def wallet_detail_url(wallet_id):
    return reverse('wallet-detail', kwargs={'pk': wallet_id})


@pytest.mark.django_db(databases=['default', 'replica'], transaction=True)
class TestWalletListCreateView:
    def test_list_wallets_authenticated_user(self, user_a_client, user_a_primary_usd_wallet, user_a_eur_wallet):
        response = user_a_client.get(WALLET_LIST_CREATE_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['count'] == 2
        wallet_ids = [wallet['id'] for wallet in response.data['data']['results']]
        assert user_a_primary_usd_wallet.id in wallet_ids
        assert user_a_eur_wallet.id in wallet_ids

    def test_list_wallets_admin_user(self, admin_client, user_a_primary_usd_wallet, user_b_primary_usd_wallet):
        response = admin_client.get(WALLET_LIST_CREATE_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['count'] >= 2
        wallet_ids = [wallet['id'] for wallet in response.data['data']['results']]
        assert user_a_primary_usd_wallet.id in wallet_ids
        assert user_b_primary_usd_wallet.id in wallet_ids

    def test_create_wallet_admin_for_other_user(self, admin_client, test_user_b, usd_currency):
        wallet_data = {"name": "User B Wallet by Admin", "currency": usd_currency.id, "user": test_user_b.id}
        response = admin_client.post(WALLET_LIST_CREATE_URL, data=wallet_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert "Wallet has been successfully created." in response.data['message']

    def test_create_wallet_unauthenticated(self, client, usd_currency):
        wallet_data = {"name": "Unauth Wallet", "currency": usd_currency.id}
        response = client.post(WALLET_LIST_CREATE_URL, data=wallet_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_wallet_invalid_data_missing_currency(self, user_a_client, test_user_a, default_tier):
        """
        This tests serializer validation before the tier logic is hit.
        """
        test_user_a.tier = default_tier
        test_user_a.save()

        wallet_data = {"name": "Test Wallet Invalid"}
        response = user_a_client.post(WALLET_LIST_CREATE_URL, data=wallet_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False
        assert 'errors' in response.data


@pytest.mark.django_db(databases=['default', 'replica'], transaction=True)
class TestWalletRetrieveUpdateDestroyView:
    def test_retrieve_wallet_owner(self, user_a_client, user_a_primary_usd_wallet):
        url = wallet_detail_url(user_a_primary_usd_wallet.id)
        response = user_a_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['id'] == user_a_primary_usd_wallet.id

    def test_retrieve_wallet_not_owner(self, user_a_client, user_b_primary_usd_wallet):
        url = wallet_detail_url(user_b_primary_usd_wallet.id)
        response = user_a_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_wallet_admin(self, admin_client, user_a_primary_usd_wallet):
        url = wallet_detail_url(user_a_primary_usd_wallet.id)
        response = admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_update_wallet_owner(self, user_a_client, user_a_primary_usd_wallet):
        url = wallet_detail_url(user_a_primary_usd_wallet.id)
        updated_data = {"name": "Updated Name by User A"}
        response = user_a_client.patch(url, data=updated_data)
        assert response.status_code == status.HTTP_200_OK
        user_a_primary_usd_wallet.refresh_from_db()
        assert user_a_primary_usd_wallet.name == "Updated Name by User A"

    def test_deactivate_wallet_owner(self, user_a_client, user_a_primary_usd_wallet):
        user_a_primary_usd_wallet.is_active = True
        user_a_primary_usd_wallet.save()
        url = wallet_detail_url(user_a_primary_usd_wallet.id)
        response = user_a_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        user_a_primary_usd_wallet.refresh_from_db()
        assert user_a_primary_usd_wallet.is_active is False

    def test_deactivate_inactive_wallet(self, user_a_client, user_a_primary_usd_wallet):
        user_a_primary_usd_wallet.is_active = False
        user_a_primary_usd_wallet.save()
        url = wallet_detail_url(user_a_primary_usd_wallet.id)
        response = user_a_client.delete(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Wallet is already inactive" in response.data['message']


@pytest.mark.django_db(databases=['default', 'replica'], transaction=True)
class TestTransactionListView:
    @pytest.fixture
    def sample_transactions(self, user_a_primary_usd_wallet, user_b_primary_usd_wallet):
        t1 = Transaction.objects.create(
            wallet=user_a_primary_usd_wallet,
            amount=Decimal("50.00"),
            transaction_type=Transaction.TransactionType.DEPOSIT,
            money_source=Transaction.MoneySource.ATM,
            status=Transaction.Status.COMPLETED,
            reference="TXNTESTA123",
        )
        t2 = Transaction.objects.create(
            wallet=user_b_primary_usd_wallet,
            amount=Decimal("30.00"),
            transaction_type=Transaction.TransactionType.DEPOSIT,
            money_source=Transaction.MoneySource.ATM,
            status=Transaction.Status.COMPLETED,
            reference="TXNTESTB456",
        )
        return t1, t2

    def test_list_transactions_authenticated_user(self, user_a_client, sample_transactions):
        t1, _ = sample_transactions
        response = user_a_client.get(TRANSACTION_LIST_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['count'] == 1
        assert response.data['data']['results'][0]['id'] == t1.id

    def test_list_transactions_admin_user(self, admin_client, sample_transactions):
        t1, t2 = sample_transactions
        response = admin_client.get(TRANSACTION_LIST_URL)
        assert response.status_code == status.HTTP_200_OK
        transaction_ids = {t['id'] for t in response.data['data']['results']}
        assert t1.id in transaction_ids
        assert t2.id in transaction_ids

    def test_list_transactions_unauthenticated(self, client):
        response = client.get(TRANSACTION_LIST_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db(databases=['default', 'replica'], transaction=True)
@patch('wallets.utils.send_sms_task')
class TestRequestATMCodeView:
    def test_request_atm_code_success(self, mock_send_sms_task, user_a_client, test_user_a):
        initial_code_count = ATMCode.objects.filter(user=test_user_a).count()
        response = user_a_client.post(REQUEST_ATM_CODE_URL)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert ATMCode.objects.filter(user=test_user_a).count() == initial_code_count + 1
        new_code = ATMCode.objects.filter(user=test_user_a).latest('created_at')
        mock_send_sms_task.delay.assert_called_once_with(
            test_user_a.phone_number,
            f"Your ATM code is {new_code.code}. Please keep it safe and do not share it with anyone.",
        )

    def test_request_atm_code_unauthenticated(self, mock_send_sms_task, client):
        response = client.post(REQUEST_ATM_CODE_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        mock_send_sms_task.delay.assert_not_called()


@pytest.mark.django_db(databases=['default', 'replica'], transaction=True)
@patch('wallets.utils.send_sms_task')
class TestTransferMoneyView:
    def test_transfer_money_success(
        self,
        mock_send_sms_task,
        user_a_client,
        test_user_a,
        user_a_primary_usd_wallet,
        user_b_primary_usd_wallet,
        default_tier,
        usd_currency,
    ):
        test_user_a.tier = default_tier
        test_user_a.save()

        TierCurrencyLimit.objects.get_or_create(
            tier=default_tier,
            currency=usd_currency,
            defaults={
                "daily_withdrawal_limit": Decimal("1000.00"),
                "daily_transfer_limit": Decimal("5000.00"),
                "daily_transactions_limit": 100,
            },
        )
        user_a_primary_usd_wallet.balance = Decimal("200.00")
        user_a_primary_usd_wallet.transferred_today = Decimal("0.00")
        user_a_primary_usd_wallet.save()

        transfer_data = {
            "source_wallet": user_a_primary_usd_wallet.id,
            "target_wallet": user_b_primary_usd_wallet.id,
            "amount": "50.00",
            "description": "Payment for services",
        }
        response = user_a_client.post(TRANSFER_MONEY_URL, data=transfer_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert "Transfer initiated successfully" in response.data['message']
        assert 'reference' in response.data['data']
        assert mock_send_sms_task.delay.call_count == 2

    def test_transfer_money_insufficient_balance(
        self, mock_send_sms_task, user_a_client, user_a_primary_usd_wallet, user_b_primary_usd_wallet
    ):
        user_a_primary_usd_wallet.balance = Decimal("10.00")
        user_a_primary_usd_wallet.save()
        transfer_data = {
            "source_wallet": user_a_primary_usd_wallet.id,
            "target_wallet": user_b_primary_usd_wallet.id,
            "amount": "100.00",
        }
        response = user_a_client.post(TRANSFER_MONEY_URL, data=transfer_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Source wallet does not have sufficient balance" in str(response.data['errors'])
        mock_send_sms_task.delay.assert_not_called()

    def test_transfer_money_exceeds_daily_limit(
        self,
        mock_send_sms_task,
        user_a_client,
        test_user_a,
        user_a_primary_usd_wallet,
        user_b_primary_usd_wallet,
        default_tier,
        usd_currency,
    ):
        test_user_a.tier = default_tier
        test_user_a.save()
        limit, _ = TierCurrencyLimit.objects.get_or_create(
            tier=default_tier,
            currency=usd_currency,
            defaults={
                "daily_transfer_limit": Decimal("100.00"),
                "daily_withdrawal_limit": 1000,
                "daily_transactions_limit": 10,
            },
        )
        limit.daily_transfer_limit = Decimal("100.00")
        limit.save()

        user_a_primary_usd_wallet.balance = Decimal("500.00")
        user_a_primary_usd_wallet.transferred_today = Decimal("0.00")
        user_a_primary_usd_wallet.save()

        transfer_data = {
            "source_wallet": user_a_primary_usd_wallet.id,
            "target_wallet": user_b_primary_usd_wallet.id,
            "amount": "150.00",
        }
        with pytest.raises(ValueError, match="Transfer limit exceeded"):
            user_a_client.post(TRANSFER_MONEY_URL, data=transfer_data)
        mock_send_sms_task.delay.assert_not_called()


@pytest.mark.django_db(databases=['default', 'replica'], transaction=True)
@patch('wallets.utils.send_sms_task')
class TestTransferActionView:
    @pytest.fixture
    def pending_transfer_ref(
        self, user_a_primary_usd_wallet, user_b_primary_usd_wallet, test_user_a, default_tier, usd_currency
    ):
        test_user_a.tier = default_tier
        test_user_a.save()
        TierCurrencyLimit.objects.get_or_create(
            tier=default_tier,
            currency=usd_currency,
            defaults={
                "daily_transfer_limit": Decimal("5000.00"),
                "daily_withdrawal_limit": 1000,
                "daily_transactions_limit": 10,
            },
        )

        user_a_primary_usd_wallet.balance = Decimal("100.00")
        user_a_primary_usd_wallet.transferred_today = Decimal("0.00")
        user_a_primary_usd_wallet.save()
        user_b_primary_usd_wallet.balance = Decimal("50.00")
        user_b_primary_usd_wallet.save()

        ref = "PACTION123"
        Transaction.objects.create(
            wallet=user_a_primary_usd_wallet,
            related_wallet=user_b_primary_usd_wallet,
            amount=Decimal("20.00"),
            status=Transaction.Status.PENDING,
            transaction_type=Transaction.TransactionType.TRANSFER_OUT,
            money_source=Transaction.MoneySource.WALLET_TO_WALLET,
            reference=ref,
        )
        Transaction.objects.create(
            wallet=user_b_primary_usd_wallet,
            related_wallet=user_a_primary_usd_wallet,
            amount=Decimal("20.00"),
            status=Transaction.Status.PENDING,
            transaction_type=Transaction.TransactionType.TRANSFER_IN,
            money_source=Transaction.MoneySource.WALLET_TO_WALLET,
            reference=ref,
        )
        return ref

    def test_transfer_action_accept_success(self, mock_send_sms_task, user_b_client, pending_transfer_ref):
        action_data = {"reference": pending_transfer_ref, "action": "accept"}
        response = user_b_client.post(TRANSFER_ACTION_URL, data=action_data)
        assert response.status_code == status.HTTP_200_OK
        assert "Transfer has been successfully Processed" in response.data['message']
        assert mock_send_sms_task.delay.call_count == 2

    def test_transfer_action_decline_success(self, mock_send_sms_task, user_b_client, pending_transfer_ref):
        action_data = {"reference": pending_transfer_ref, "action": "decline"}
        response = user_b_client.post(TRANSFER_ACTION_URL, data=action_data)
        assert response.status_code == status.HTTP_200_OK
        assert "Transfer has been successfully Declined" in response.data['message']
        assert mock_send_sms_task.delay.call_count == 2

    def test_transfer_action_finalize_raises_value_error(self, mock_send_sms_task, user_a_client):
        action_data = {"reference": "NONEXISTENTREF", "action": "accept"}
        response = user_a_client.post(TRANSFER_ACTION_URL, data=action_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No pending transaction found" in response.data['message']
        mock_send_sms_task.delay.assert_not_called()


@pytest.mark.django_db(databases=['default', 'replica'], transaction=True)
@patch('wallets.utils.send_sms_task')
class TestCancelTransferView:
    @pytest.fixture
    def pending_cancellable_ref(self, user_a_primary_usd_wallet, user_b_primary_usd_wallet):
        ref = "PCANCEL123"
        Transaction.objects.create(
            wallet=user_a_primary_usd_wallet,
            related_wallet=user_b_primary_usd_wallet,
            amount=Decimal("25.00"),
            status=Transaction.Status.PENDING,
            transaction_type=Transaction.TransactionType.TRANSFER_OUT,
            reference=ref,
            money_source=Transaction.MoneySource.WALLET_TO_WALLET,
        )
        Transaction.objects.create(
            wallet=user_b_primary_usd_wallet,
            related_wallet=user_a_primary_usd_wallet,
            amount=Decimal("25.00"),
            status=Transaction.Status.PENDING,
            transaction_type=Transaction.TransactionType.TRANSFER_IN,
            reference=ref,
            money_source=Transaction.MoneySource.WALLET_TO_WALLET,
        )
        return ref

    def test_cancel_transfer_success(self, mock_send_sms_task, user_a_client, pending_cancellable_ref):
        cancel_data = {"reference": pending_cancellable_ref}
        response = user_a_client.post(CANCEL_TRANSFER_URL, data=cancel_data)
        assert response.status_code == status.HTTP_200_OK
        assert "Transfer has been successfully canceled" in response.data['message']
        assert mock_send_sms_task.delay.call_count == 2

    def test_cancel_transfer_raises_value_error(self, mock_send_sms_task, user_a_client):
        cancel_data = {"reference": "NONEXISTENTREF"}
        response = user_a_client.post(CANCEL_TRANSFER_URL, data=cancel_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No pending transactions found" in response.data['message']
        mock_send_sms_task.delay.assert_not_called()


@pytest.mark.django_db(databases=['default', 'replica'], transaction=True)
@patch('wallets.utils.send_sms_task')
class TestBankWebhook:
    def test_bank_webhook_valid_signature_success_event(
        self, mock_send_sms_task_global, client, user_a_primary_usd_wallet
    ):

        event_data = {"type": "deposit", "wallet_id": user_a_primary_usd_wallet.id, "amount": "100.00"}
        response = client.post(
            BANK_WEBHOOK_URL, data=event_data, content_type='application/json', HTTP_X_WEBHOOK_TOKEN='supersecrettoken'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] == True
        mock_send_sms_task_global.delay.assert_called_once()

    def test_bank_webhook_valid_signature_failed_event(self, mock_send_sms_task_global, client):

        event_data = {"type": "unknown_event", "data": {}}
        response = client.post(
            BANK_WEBHOOK_URL, data=event_data, content_type='application/json', HTTP_X_WEBHOOK_TOKEN='supersecrettoken'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        mock_send_sms_task_global.delay.assert_not_called()

    def test_bank_webhook_invalid_signature(self, mock_send_sms_task_global, client):
        event_data = {"type": "test", "data": {}}
        response = client.post(
            BANK_WEBHOOK_URL, data=event_data, content_type='application/json', HTTP_X_WEBHOOK_TOKEN='wrongtoken'
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data == {"success": False, "message": "Invalid signature."}

    def test_bank_webhook_integration_atm_deposit_success(
        self, mock_send_sms_task_in_utils, client, user_a_primary_usd_wallet
    ):

        initial_balance = user_a_primary_usd_wallet.balance
        deposit_amount = Decimal("75.00")

        event_data = {"type": "deposit", "wallet_id": user_a_primary_usd_wallet.id, "amount": str(deposit_amount)}

        response = client.post(
            BANK_WEBHOOK_URL, data=event_data, content_type='application/json', HTTP_X_WEBHOOK_TOKEN='supersecrettoken'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['message'] == 'Money recieved successfully'

        user_a_primary_usd_wallet.refresh_from_db()
        assert user_a_primary_usd_wallet.balance == initial_balance + deposit_amount

        mock_send_sms_task_in_utils.delay.assert_called_once()
