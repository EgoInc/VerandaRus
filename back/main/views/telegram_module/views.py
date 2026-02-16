from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from main.models.telegram import TelegramChat
from main.models.bookings import Booking  # проверь путь к модели
from .serializers import TelegramChatSerializer
from .bot import send_telegram_message
from ..permissions import IsAdminUser


class LinkTelegramView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TelegramChatSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chat_id = serializer.validated_data['chat_id']
        obj, created = TelegramChat.objects.update_or_create(
            user=request.user,
            defaults={'chat_id': chat_id}
        )
        return Response({'status': 'linked', 'chat_id': chat_id})


class UnlinkTelegramView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        TelegramChat.objects.filter(user=request.user).delete()
        return Response({'status': 'unlinked'})


class TestNotificationView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = TelegramChatSerializer

    def post(self, request):
        chat_id = request.data.get('chat_id')
        text = request.data.get('text', 'Тестовое сообщение')
        if not chat_id:
            return Response(
                {'error': 'chat_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        result = send_telegram_message(chat_id, text)
        if result and result.get('ok'):
            return Response({'status': 'sent'})
        return Response(
            {'error': 'Ошибка отправки'},
            status=status.HTTP_502_BAD_GATEWAY
        )


class DailyDigestView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        tomorrow = timezone.now().date() + timedelta(days=1)
        bookings = Booking.objects.filter(
            check_in__date=tomorrow,
            status__in=['CONFIRMED']
        )
        if not bookings.exists():
            return Response({'message': 'Нет броней на завтра'})
        houses = bookings.values_list('accommodation__title', flat=True).distinct()
        message = f"Завтра заняты: {', '.join(houses)}"
        admin_chat_id = request.data.get('admin_chat_id')
        if admin_chat_id:
            send_telegram_message(admin_chat_id, message)
        return Response({'status': 'digest sent', 'houses': list(houses)})