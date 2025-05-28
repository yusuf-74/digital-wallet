from celery import shared_task
from django.core.mail import EmailMultiAlternatives


@shared_task
def send_email_task(email, subject, body="", html=None):
    """
    Task to send an email asynchronously.

    :param email: Recipient's email address
    :param body: Body of the email
    """
    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        to=[email],
    )
    if html:
        email.attach_alternative(html, "text/html")
    email.send()
    return f"Email sent to {email} with subject '{subject}'"


@shared_task
def send_sms_task(phone_number, message):
    """
    Task to send an SMS asynchronously.

    :param phone_number: Recipient's phone number
    :param message: Message to be sent
    """
    # using Twilio or any other SMS service would be implemented here
    print(f"Sending SMS to {phone_number}: {message}")
    return f"SMS sent to {phone_number}: {message}"
