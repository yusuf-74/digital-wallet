from decimal import Decimal

from decouple import config
from django.db.transaction import atomic

from authentication.models import User
from utils.common_tasks import send_sms_task
from utils.data_generators import generate_reference

from .models import Transaction, Wallet


class TransactionOperator:
    @staticmethod
    def initiate_wallet_to_wallet_transfer(source: Wallet, target: Wallet, amount: int, description: str) -> str:
        with atomic():

            # check if source wallet didn't exceed the limit
            transferred_today = source.transferred_today
            daily_transfer_limit = (
                source.user.tier.currency_limits.filter(currency=source.currency).first().daily_transfer_limit
            )

            if transferred_today + amount > daily_transfer_limit:
                raise ValueError(
                    f"Transfer limit exceeded. You can only transfer {daily_transfer_limit - transferred_today} {source.currency.currency_code} today."
                )

            reference = generate_reference(prefix="WTRF")

            source_transaction = Transaction.objects.create(
                wallet=source,
                related_wallet=target,
                amount=amount,
                status=Transaction.Status.PENDING,
                transaction_type=Transaction.TransactionType.TRANSFER_OUT,
                money_source=Transaction.MoneySource.WALLET_TO_WALLET,
                description=description,
                reference=reference,
            )
            source_transaction.save()
            target_transaction = Transaction.objects.create(
                wallet=target,
                related_wallet=source,
                amount=amount,
                status=Transaction.Status.PENDING,
                transaction_type=Transaction.TransactionType.TRANSFER_IN,
                money_source=Transaction.MoneySource.WALLET_TO_WALLET,
                description=description,
                reference=reference,
            )
            target_transaction.save()
            return reference

    @staticmethod
    def finalize_transfer(reference: str, action: str, actor: User) -> None:
        with atomic():
            transaction = Transaction.objects.filter(
                reference=reference,
                status=Transaction.Status.PENDING,
                transaction_type=Transaction.TransactionType.TRANSFER_OUT,
                related_wallet__user=actor,
            ).first()
            if not transaction:
                raise ValueError("No pending transaction found with the provided reference.")
            amount = transaction.amount
            source = transaction.wallet
            target = transaction.related_wallet
            transferred_today = source.transferred_today
            daily_transfer_limit = (
                source.user.tier.currency_limits.filter(currency=source.currency).first().daily_transfer_limit
            )

            if transferred_today + amount > daily_transfer_limit:
                Transaction.objects.filter(
                    reference=reference,
                    status=Transaction.Status.PENDING,
                    transaction_type=Transaction.TransactionType.TRANSFER_OUT,
                    wallet=source,
                    related_wallet=target,
                ).update(status=(Transaction.Status.COMPLETED if action == 'ACCEPT' else Transaction.Status.FAILED))
                Transaction.objects.filter(
                    reference=reference,
                    status=Transaction.Status.PENDING,
                    transaction_type=Transaction.TransactionType.TRANSFER_IN,
                    wallet=target,
                    related_wallet=source,
                ).update(status=(Transaction.Status.COMPLETED if action == 'ACCEPT' else Transaction.Status.FAILED))
                NotificationOperator.send_transfer_failed_notification(source, target, amount, reference)
                raise ValueError(
                    f"Transfer limit exceeded. You can only transfer {daily_transfer_limit - transferred_today} {source.currency} today."
                )

            if not transaction:
                raise ValueError("No pending transactions found with the provided reference.")

            source = transaction.wallet
            target = transaction.related_wallet
            if action == 'accept':
                if source.balance < transaction.amount:
                    raise ValueError("Insufficient balance in source wallet.")

                source.balance -= transaction.amount
                source.transferred_today += transaction.amount
                target.balance += transaction.amount
                source.save()
                target.save()
                NotificationOperator.send_transfer_accepted_notification(source, target, amount, reference)
            else:
                NotificationOperator.send_transfer_declined_notification(source, target, amount, reference)
            # Update the status of both transactions
            Transaction.objects.filter(
                reference=reference,
                status=Transaction.Status.PENDING,
                transaction_type=Transaction.TransactionType.TRANSFER_OUT,
                wallet=source,
                related_wallet=target,
            ).update(status=(Transaction.Status.COMPLETED if action == 'ACCEPT' else Transaction.Status.DECLINED))
            Transaction.objects.filter(
                reference=reference,
                status=Transaction.Status.PENDING,
                transaction_type=Transaction.TransactionType.TRANSFER_IN,
                wallet=target,
                related_wallet=source,
            ).update(status=(Transaction.Status.COMPLETED if action == 'ACCEPT' else Transaction.Status.DECLINED))

    @staticmethod
    def cancel_transfer(reference: str, actor: User) -> None:
        with atomic():
            transaction = Transaction.objects.filter(
                reference=reference,
                status=Transaction.Status.PENDING,
                transaction_type=Transaction.TransactionType.TRANSFER_OUT,
                wallet__user=actor,
            ).first()
            if not transaction:
                raise ValueError("No pending transactions found with the provided reference.")
            source = transaction.wallet
            target = transaction.related_wallet

            NotificationOperator.send_transfer_canceled_notification(
                transaction.wallet, transaction.related_wallet, transaction.amount, reference
            )
            Transaction.objects.filter(
                reference=reference,
                status=Transaction.Status.PENDING,
                transaction_type=Transaction.TransactionType.TRANSFER_OUT,
                wallet=source,
                related_wallet=target,
            ).update(status=(Transaction.Status.CANCELED))
            Transaction.objects.filter(
                reference=reference,
                status=Transaction.Status.PENDING,
                transaction_type=Transaction.TransactionType.TRANSFER_IN,
                wallet=target,
                related_wallet=source,
            ).update(status=(Transaction.Status.CANCELED))

    @staticmethod
    def atm_deposit(target: Wallet, amount: Decimal) -> Transaction:
        with atomic():
            transaction = Transaction.objects.create(
                wallet=target,
                amount=amount,
                status=Transaction.Status.COMPLETED,
                transaction_type=Transaction.TransactionType.DEPOSIT,
                money_source=Transaction.MoneySource.ATM,
            )
            target.balance += amount
            target.save()

        return transaction

    @staticmethod
    def atm_withdrawal(source: Wallet, amount: Decimal) -> Transaction:
        with atomic():
            daily_withdrawal_limit = (
                source.user.tier.currency_limits.filter(currency=source.currency).first().daily_withdrawal_limit
            )
            if source.withdrawn_today + amount > daily_withdrawal_limit:
                raise ValueError(
                    f"Withdrawal limit exceeded. You can only withdraw {daily_withdrawal_limit - source.withdrawn_today} {source.currency} today."
                )

            if source.balance < amount:
                raise ValueError("Insufficient balance")

            transaction = Transaction.objects.create(
                wallet=source,
                amount=amount,
                status=Transaction.Status.COMPLETED,
                transaction_type=Transaction.TransactionType.WITHDRAWAL,
                money_source=Transaction.MoneySource.ATM,
            )

            source.balance -= amount
            source.withdrawn_today += transaction.amount
            source.save()

        return transaction

    @staticmethod
    def bank_transfer_out(source: Wallet, amount: Decimal):
        with atomic():
            daily_transfer_limit = (
                source.user.tier.currency_limits.filter(currency=source.currency).first().daily_transfer_limit
            )
            if source.transferred_today + amount > daily_transfer_limit:
                raise ValueError(
                    f"Transfer limit exceeded. You can only transfer {daily_transfer_limit - source.transferred_today} {source.currency} today."
                )
            if source.balance < amount:
                raise ValueError("Insufficient Balance")

            transaction = Transaction.objects.create(
                wallet=source,
                amount=amount,
                status=Transaction.Status.COMPLETED,
                transaction_type=Transaction.TransactionType.TRANSFER_OUT,
                money_source=Transaction.MoneySource.BANK_TRANSFER,
            )

            source.balance -= amount
            source.transferred_today += transaction.amount
            source.save()

        return transaction


class NotificationOperator:
    @staticmethod
    def send_transfer_notification(source: Wallet, target: Wallet, amount: int, reference: str) -> None:
        sender_message = f"""
        Hi {target.user.first_name}, you have initiated a transfer of {source.currency} {amount} to {target.user.first_name} {target.user.last_name} ({target.user.phone_number}). 
        The transaction reference is {reference}.
        Waiting for Receiver to accept the transfer from your wallet {source.name}"""

        receiver_message = f"Hi {source.user.first_name}, you have a pending transfer of {source.currency} {amount} from {source.user.first_name} {source.user.last_name} ({source.user.phone_number}). You can accept the transfer through the app."

        send_sms_task.delay(source.user.phone_number, sender_message)
        send_sms_task.delay(target.user.phone_number, receiver_message)

    @staticmethod
    def send_transfer_accepted_notification(source: Wallet, target: Wallet, amount: int, reference: str) -> None:
        sender_message = f"Hi {source.user.first_name}, your transfer of {source.currency} {amount} to {target.user.first_name} {target.user.last_name} ({target.user.phone_number}) has been accepted. The transaction reference is {reference}."
        receiver_message = f"Hi {target.user.first_name}, you've accepted a transfer of {source.currency} {amount} from {source.user.first_name} {source.user.last_name} ({source.user.phone_number}). The transaction reference is {reference}."

        send_sms_task.delay(source.user.phone_number, sender_message)
        send_sms_task.delay(target.user.phone_number, receiver_message)

    @staticmethod
    def send_transfer_declined_notification(source: Wallet, target: Wallet, amount: int, reference: str) -> None:
        sender_message = f"Hi {source.user.first_name}, your transfer of {source.currency} {amount} to {target.user.first_name} {target.user.last_name} ({target.user.phone_number}) has been declined. The transaction reference is {reference}."
        receiver_message = f"Hi {target.user.first_name}, you've declined a transfer of {source.currency} {amount} from {source.user.first_name} {source.user.last_name} ({source.user.phone_number}). The transaction reference is {reference}."

        send_sms_task.delay(source.user.phone_number, sender_message)
        send_sms_task.delay(target.user.phone_number, receiver_message)

    @staticmethod
    def send_transfer_canceled_notification(source: Wallet, target: Wallet, amount: int, reference: str) -> None:
        sender_message = f"Hi {source.user.first_name}, your transfer of {source.currency} {amount} to {target.user.first_name} {target.user.last_name} ({target.user.phone_number}) has been canceled. The transaction reference is {reference}."
        receiver_message = f"Hi {target.user.first_name}, a transfer of {source.currency} {amount} from {source.user.first_name} {source.user.last_name} ({source.user.phone_number}) has been canceled. The transaction reference is {reference}."
        send_sms_task.delay(source.user.phone_number, sender_message)
        send_sms_task.delay(target.user.phone_number, receiver_message)

    @staticmethod
    def send_transfer_failed_notification(source: Wallet, target: Wallet, amount: int, reference: str) -> None:
        sender_message = f"Hi {source.user.first_name}, your transfer of {source.currency} {amount} to {target.user.first_name} {target.user.last_name} ({target.user.phone_number}) has failed. The transaction reference is {reference}."
        receiver_message = f"Hi {target.user.first_name}, a transfer of {source.currency} {amount} from {source.user.first_name} {source.user.last_name} ({source.user.phone_number}) has failed. The transaction reference is {reference}."

        send_sms_task.delay(source.user.phone_number, sender_message)
        send_sms_task.delay(target.user.phone_number, receiver_message)

    @staticmethod
    def send_atm_code(phone_number, code):
        send_sms_task.delay(
            phone_number, f"Your ATM code is {code}. Please keep it safe and do not share it with anyone."
        )

    @staticmethod
    def send_withdrawal_notification(transaction: Transaction):
        message = f"You've successfully withdrawed {transaction.wallet.currency} {transaction.amount} from your wallet {transaction.wallet.name}. transaction reference {transaction.reference}"
        send_sms_task.delay(transaction.wallet.user.phone_number, message)

    @staticmethod
    def send_deposit_notification(transaction: Transaction):
        message = f"You've successfully deposited {transaction.wallet.currency} {transaction.amount} to your wallet {transaction.wallet.name}. transaction reference {transaction.reference}"
        send_sms_task.delay(transaction.wallet.user.phone_number, message)

    @staticmethod
    def send_bank_transfer_in_notification(transaction: Transaction):
        message = f"You've received {transaction.wallet.currency} {transaction.amount} to your wallet {transaction.wallet.name} from bank transfer. transaction reference {transaction.reference}"
        send_sms_task.delay(transaction.wallet.user.phone_number, message)

    @staticmethod
    def send_bank_transfer_out_notification(transaction: Transaction):
        message = f"You've sent {transaction.wallet.currency} {transaction.amount} from your wallet {transaction.wallet.name} through bank transfer. transaction reference {transaction.reference}"
        send_sms_task.delay(transaction.wallet.user.phone_number, message)


def verify_webhook_signature(request):
    secret_token = config("WEBHOOK_SECRET", "supersecrettoken")
    received_token = request.headers.get("X-Webhook-Token")

    return received_token == secret_token
