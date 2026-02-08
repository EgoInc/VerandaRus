from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    BlacklistedPhoneSerializer,
    MyBookingSerializer,
    DevLoginSerializer,
    DevLoginResponseSerializer,
    AuthorizationSerializer,
    AuthorizationResponseSerializer,
)


class MyBookingsView(APIView):
    """Return bookings for current user (TODO implementation)."""

    serializer_class = MyBookingSerializer

    def get(self, request):
        # TODO: return bookings for current user
        return Response(
            {"detail": "TODO: implement my bookings list"},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )


class BlacklistCreateView(APIView):
    """Add phone to blacklist (TODO implementation)."""

    serializer_class = BlacklistedPhoneSerializer

    def post(self, request):
        # TODO: add phone to blacklist with reason
        return Response(
            {"detail": "TODO: implement blacklist create"},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )


class DevLoginView(APIView):
    """DEV ONLY: create/get a user by login and return a token."""

    serializer_class = DevLoginSerializer

    @extend_schema(request=DevLoginSerializer, responses=DevLoginResponseSerializer)
    def post(self, request):
        # WARNING: DEV ONLY. This bypasses password checks and SMS verification.
        serializer = DevLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        login = serializer.validated_data["login"]

        # Create or fetch user by username.
        User = get_user_model()
        user, _created = User.objects.get_or_create(username=login, defaults={"email": ""})

        # Create or fetch DRF token.
        token, _created = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user_id": user.id,
                "username": user.username,
            },
            status=status.HTTP_200_OK,
        )


class AuthorizationView(APIView):
    """Authorize by phone and return JWT tokens (password ignored for now)."""

    serializer_class = AuthorizationSerializer

    @extend_schema(
        summary="Авторизация",
        description="Принимает номер телефона и пароль (пароль пока не проверяется).",
        request=AuthorizationSerializer,
        responses=AuthorizationResponseSerializer,
        tags=["authorization"],
        operation_id="authorization",
    )
    def post(self, request):
        serializer = AuthorizationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]

        User = get_user_model()
        user, _created = User.objects.get_or_create(
            phone=phone,
            defaults={
                "username": phone,
                "email": "",
            },
        )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user_id": user.id,
                "phone": user.phone or phone,
            },
            status=status.HTTP_200_OK,
        )
