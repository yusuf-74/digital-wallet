import random
import uuid

from django.utils import timezone


def generate_username(first_name, last_name, separator='_'):
    user_name = (
        first_name.replace(' ', separator)
        + separator
        + last_name.replace(' ', separator)
        + str(random.randint(1, 999999))
    )
    user_name = user_name.lower()
    return user_name


def generate_password():
    all_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890#$%&@!^*'
    password = []
    for _ in range(12):
        password.append(random.choice(all_chars))
    return ''.join(password)


def generate_otp():
    return random.randint(100000, 999999)


def generate_reference(prefix=None):
    timestamp = timezone.now().strftime("%Y%m%d%H%M%S")  # TZ-aware
    uid = uuid.uuid4().hex[:8].upper()
    return f"{prefix}-{timestamp}-{uid}" if prefix else f"{timestamp}-{uid}"


def generate_unique_wallet_name(existing_names, currency):
    base = f"{currency} Wallet"

    if base not in existing_names:
        return base
    i = 2
    while f"{base} {i}" in existing_names:
        i += 1
    return f"{base} {i}"
