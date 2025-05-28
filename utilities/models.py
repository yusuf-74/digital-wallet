from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models

MESSAGES_TYPE = (
    ('success', 'Success'),
    ('info', 'Info'),
    ('warning', 'Warning'),
    ('danger', 'Danger'),
)


class SystemMessage(models.Model):
    schema = 'default'

    message = models.TextField()

    groups = models.ManyToManyField(Group, related_name='system_messages')
    is_restricted = models.BooleanField(default=False)
    release_date = models.DateTimeField()
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.BooleanField(default=True)
    message_type = models.CharField(max_length=10, choices=MESSAGES_TYPE, default='info')
    last_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='updated_system_messages'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'system_messages'
        verbose_name = 'System Message'
        ordering = ['-release_date']

    def __str__(self):
        return self.message


class Currency(models.Model):
    currency_code = models.CharField(max_length=10, unique=True)
    currency_name = models.CharField(max_length=50, unique=True)
    symbol = models.CharField(max_length=10, unique=True)
    last_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='updated_currencies'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'currencies'
        ordering = ['-id']

    def __str__(self):
        return f"{self.currency_name} ({self.symbol})"
