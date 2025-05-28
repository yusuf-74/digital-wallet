from celery import shared_task

from .models import Wallet


@shared_task
def set_wallets_spends():
    wallets = Wallet.objects.all()

    for wallet in wallets:
        wallet.transferred_today = 0
        wallet.withdrawn_today = 0
        wallet.save()
    return f"Updated {len(wallets)} wallets for today's spends."
