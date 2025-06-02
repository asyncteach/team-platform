# auth_service/accounts/utils.py

from django.template.loader import render_to_string
from .models import EmailConfirmationCode
from random import randint
from django.utils import timezone
from datetime import timedelta
from accounts.tasks import send_email_task

def can_send_code(user, purpose):
    last = EmailConfirmationCode.objects.filter(user=user, purpose=purpose).order_by('-created_at').first()
    return not last or timezone.now() - last.created_at > timedelta(minutes=1)


def send_confirmation_email(user, purpose):
    if not can_send_code(user, purpose):
        return False

    code = f"{randint(1000, 9999)}"
    EmailConfirmationCode.objects.create(user=user, code=code, purpose=purpose)

    subject = {
        'register': 'Подтверждение регистрации',
        'reset_password': 'Сброс пароля',
        'change_email': 'Подтверждение смены email',
    }.get(purpose, 'Подтверждение')

    template_name = {
        'register': 'confirmation_email.html',
        'reset_password': 'reset_password.html',
        'change_email': 'change_email.html',
    }.get(purpose, 'confirmation_email.html')

    html_message = render_to_string(template_name, {
        'code': code,
    })

    send_email_task.delay(
        subject=subject,
        message='',  # пустое, т.к. используем html
        recipient_list=[user.email],
        html_message=html_message
    )

    return True
