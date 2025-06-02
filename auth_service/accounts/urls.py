# auth_service/accounts/urls.py


from django.urls import path
from .api import RegisterAPIView
from .api import VerifyCodeAPIView
from .api import protected_view
from .api import logout_view
from .api import (
    RequestResetPasswordAPIView,
    VerifyResetCodeAPIView,
    SetNewPasswordAPIView,
)

urlpatterns = [
    path('api/register/', RegisterAPIView.as_view(), name='api_register'), # Регистрация
    path('api/verify-code/', VerifyCodeAPIView.as_view(), name='api_verify_code'), # Подтверждение Email по коду
    path('api/protected/', protected_view, name='protected'), # Проверка авторизации
    path('api/logout/', logout_view, name='api_logout'), # Выход с инвалидом refresh-токеном
    path('api/request-reset/', RequestResetPasswordAPIView.as_view(), name='request_reset'), # Ещё не добавлен 
    path('api/verify-reset-code/', VerifyResetCodeAPIView.as_view(), name='verify_reset_code'), # Подтверждение сброса кода
    path('api/set-new-password/', SetNewPasswordAPIView.as_view(), name='set_new_password'), # Установка нового пароля
]


from accounts.jwt_views import CustomTokenObtainPairView, CustomTokenRefreshView

urlpatterns += [
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]



from accounts.api import RequestEmailChangeAPIView, ConfirmEmailChangeAPIView

urlpatterns += [
    path('api/request-email-change/', RequestEmailChangeAPIView.as_view(), name='request_email_change'),
    path('api/confirm-email-change/', ConfirmEmailChangeAPIView.as_view(), name='confirm_email_change'),
]
