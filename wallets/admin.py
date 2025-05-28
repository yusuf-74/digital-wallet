from django.contrib import admin

from .models import ATMCode, Tier, TierCurrencyLimit, Transaction, Wallet

admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(ATMCode)
admin.site.register(Tier)
admin.site.register(TierCurrencyLimit)
