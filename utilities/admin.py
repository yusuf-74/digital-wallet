from django.contrib import admin

from .models import Currency, SystemMessage

admin.site.register(SystemMessage)
admin.site.register(Currency)
