# auth_service/accounts/tasks.py

from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_email_task(subject, message, recipient_list, html_message=None):
    send_mail(
        subject=subject,
        message=message,
        from_email=None,
        recipient_list=recipient_list,
        html_message=html_message
    )
