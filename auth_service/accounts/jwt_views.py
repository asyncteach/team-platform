# auth_service/accounts/jwt_views.py

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse

# 🔐 Кастомный вход с email/username + password
@extend_schema(
    summary="Получение JWT токенов (вход)",
    description="Принимает username и пароль, возвращает access и refresh токены.",
    request=TokenObtainPairSerializer,
    responses={
        200: OpenApiResponse(description="Успешный вход и получение токенов"),
        401: OpenApiResponse(description="Неверные учетные данные"),
    }
)
class CustomTokenObtainPairView(TokenObtainPairView):
    pass


# 🔄 Обновление access-токена по refresh-токену
@extend_schema(
    summary="Обновление access-токена",
    description="Принимает refresh-токен и возвращает новый access-токен.",
    request=TokenRefreshSerializer,
    responses={
        200: OpenApiResponse(description="Новый access-токен получен"),
        401: OpenApiResponse(description="Недействительный или просроченный refresh-токен"),
    }
)
class CustomTokenRefreshView(TokenRefreshView):
    pass


from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from accounts.serializers import EmailTokenObtainPairSerializer  # путь подстрой под себя

@extend_schema(
    summary="Вход по email и паролю",
    description="Возвращает JWT access/refresh токены. Требует email и пароль.",
    request=EmailTokenObtainPairSerializer,
    responses={
        200: OpenApiResponse(description="Успешный вход"),
        401: OpenApiResponse(description="Неверные учетные данные"),
    }
)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


@extend_schema(
    summary="Обновление access токена",
    description="Передаётся refresh токен, возвращается новый access токен.",
)
class CustomTokenRefreshView(TokenRefreshView):
    pass
