from celery import shared_task

from .models import OTP


@shared_task
def delete_expired_otp_codes():
    codes = OTP.objects.all()
    deleted_count = 0
    for code in codes:
        if not code.is_valid():
            code.delete()
            deleted_count += 1
    return f"Deleted {deleted_count} expired OTP codes."
