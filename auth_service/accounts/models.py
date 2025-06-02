# auth_service/accounts/models.py


from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_email_confirmed = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'            # Логинимся по email
    REQUIRED_FIELDS = ['username']      # username обязателен, но не для логина


    
# Для подтверждающего кода

class EmailConfirmationCode(models.Model): # Это таблица для хранения кода
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE) # Один пользователь может иметь много кодов, если удалим пользователя, то удалим и коды
    code = models.CharField(max_length=4) #  Это просто строка длиной 4 символа (код)
    created_at = models.DateTimeField(auto_now_add=True) # Когда был создан код Django сам припишет дату
    purpose = models.CharField(max_length=50)  # Используется для определения = с какой целью запрашивают код
    
    
# Для смены Email
    

class EmailChangeRequest(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    new_email = models.EmailField()
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        from django.utils import timezone
        from datetime import timedelta
        return self.created_at < timezone.now() - timedelta(minutes=10)
