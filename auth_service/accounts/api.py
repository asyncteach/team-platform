# auth_service/accounts/api.py


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser, EmailConfirmationCode
from datetime import timedelta
from django.utils import timezone


from .serializers import RegisterSerializer, VerifyCodeSerializer
from .utils import send_confirmation_email
from django.contrib.auth import login

from drf_spectacular.utils import extend_schema, OpenApiResponse
from accounts.tasks import send_email_task



@extend_schema(
    summary="Регистрация пользователя",
    description="Создаёт нового пользователя и отправляет код подтверждения на email. "
                "Пользователь временно неактивен.",
    request=RegisterSerializer,
    responses={
        201: OpenApiResponse(response={'message': 'Пользователь создан. Код отправлен на почту.'}),
        400: OpenApiResponse(response={'error': 'Некорректные данные'})
    }
)
class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_confirmation_email(user, purpose='register')
            return Response({
                'message': 'Пользователь создан. Код отправлен на почту.',
                'user_id': user.id
            }, status=201)
        return Response(serializer.errors, status=400)



@extend_schema(
    summary="Подтверждение email-кода",
    description="Подтверждает email по 4-значному коду. После этого пользователь активируется и выполняется вход.",
    request=VerifyCodeSerializer,
    responses={
        200: OpenApiResponse(response={'message': 'Email подтвержден, вход выполнен'}),
        400: OpenApiResponse(response={'error': 'Неверный или просроченный код'}),
    }
)
class VerifyCodeAPIView(APIView):
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.is_active = True
            user.is_email_confirmed = True
            user.save()
            login(request, user)
            return Response({'message': 'Email подтвержден, вход выполнен'}, status=200)
        return Response(serializer.errors, status=400)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@extend_schema(
    summary="Проверка авторизации",
    description="Доступ только для авторизованных пользователей. Требуется access-токен.",
    responses={200: OpenApiResponse(response={'message': 'Привет, <username>! Ты авторизован.'})}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({'message': f'Привет, {request.user.username}! Ты авторизован.'})





from rest_framework_simplejwt.tokens import RefreshToken, TokenError

@extend_schema(
    summary="Выход (Logout)",
    description="Инвалидирует refresh токен. Пользователь должен быть авторизован.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'refresh': {'type': 'string', 'example': 'eyJ...'}
            },
            'required': ['refresh']
        }
    },
    responses={
        205: OpenApiResponse(response={'message': 'Вы успешно вышли из системы'}),
        400: OpenApiResponse(response={'error': 'Недействительный токен'})
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({'error': 'Refresh токен обязателен'}, status=400)
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Вы успешно вышли из системы'}, status=205)
    except TokenError:
        return Response({'error': 'Недействительный или просроченный токен'}, status=400)



class VerifyResetCodeAPIView(APIView):
    @extend_schema(
        summary="Подтверждение кода сброса",
        description="Подтверждает 4-значный код. Если код корректный — возвращает user_id.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string', 'example': 'user@example.com'},
                    'code': {'type': 'string', 'example': '1234'}
                },
                'required': ['email', 'code']
            }
        },
        responses={
            200: OpenApiResponse(response={'user_id': 1}),
            400: OpenApiResponse(response={'error': 'Неверный или просроченный код'})
        }
    )
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=404)

        code_obj = EmailConfirmationCode.objects.filter(
            user=user,
            purpose='reset_password',
            created_at__gte=timezone.now() - timedelta(minutes=10)
        ).order_by('-created_at').first()

        if code_obj and code_obj.code == code:
            return Response({'user_id': user.id}, status=200)
        return Response({'error': 'Неверный или просроченный код'}, status=400)


class SetNewPasswordAPIView(APIView):
    @extend_schema(
        summary="Установка нового пароля",
        description="Устанавливает новый пароль по user_id и паролю (дважды).",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'user_id': {'type': 'integer', 'example': 1},
                    'password1': {'type': 'string', 'example': 'newpass123'},
                    'password2': {'type': 'string', 'example': 'newpass123'}
                },
                'required': ['user_id', 'password1', 'password2']
            }
        },
        responses={
            200: OpenApiResponse(response={'message': 'Пароль успешно обновлён'}),
            400: OpenApiResponse(response={'error': 'Пароли не совпадают или пользователь не найден'})
        }
    )
    def post(self, request):
        user_id = request.data.get('user_id')
        password1 = request.data.get('password1')
        password2 = request.data.get('password2')

        if password1 != password2:
            return Response({'error': 'Пароли не совпадают'}, status=400)

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=404)

        user.set_password(password1)
        user.save()
        return Response({'message': 'Пароль успешно обновлён'}, status=200)



from .serializers import EmailChangeRequestSerializer, ConfirmEmailChangeSerializer
from rest_framework.permissions import IsAuthenticated
from .models import EmailChangeRequest
from random import randint
from django.core.mail import send_mail
from drf_spectacular.utils import extend_schema


@extend_schema(
    summary="Запрос на смену email",
    description="Принимает пароль и новый email. Проверяет пароль, отправляет код на новый email.",
    request=EmailChangeRequestSerializer,
    responses={200: OpenApiResponse(response={"message": "Код подтверждения отправлен на новый email"})}
)
class RequestEmailChangeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EmailChangeRequestSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            new_email = serializer.validated_data['new_email']

            code = f"{randint(1000, 9999)}"
            EmailChangeRequest.objects.create(user=user, new_email=new_email, code=code)

            send_email_task.delay(
                "Код подтверждения смены email",
                f"Ваш код подтверждения: {code}",
                [new_email]
            )


            return Response({"message": "Код подтверждения отправлен на новый email"}, status=200)

        return Response(serializer.errors, status=400)


@extend_schema(
    summary="Подтверждение кода и смена email",
    description="Подтверждает код и меняет email пользователя на новый.",
    request=ConfirmEmailChangeSerializer,
    responses={200: OpenApiResponse(response={"message": "Email успешно обновлён"})}
)
class ConfirmEmailChangeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ConfirmEmailChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            new_email = serializer.validated_data['new_email']
            serializer.validated_data['request_obj'].delete()

            user.email = new_email
            user.save()

            return Response({"message": "Email успешно обновлён"}, status=200)

        return Response(serializer.errors, status=400)




class RequestResetPasswordAPIView(APIView):
    @extend_schema(
        summary="Запрос на сброс пароля",
        description="Отправляет 4-значный код подтверждения на указанный email, если пользователь существует.",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string', 'example': 'user@example.com'}
                },
                'required': ['email']
            }
        },
        responses={
            200: OpenApiResponse(response={'message': 'Код отправлен на email'}),
            404: OpenApiResponse(response={'error': 'Пользователь с таким email не найден'})
        }
    )
    def post(self, request):
        email = request.data.get('email')
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Пользователь с таким email не найден'}, status=404)

        success = send_confirmation_email(user, purpose='reset_password')
        if success:
            return Response({'message': 'Код отправлен на email'}, status=200)
        return Response({'error': 'Слишком частые попытки. Подождите немного.'}, status=429)

