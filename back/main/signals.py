from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models.bookings import Booking
from .models.telegram import TelegramChat
from .views.telegram_module.bot import send_telegram_message

@receiver(post_save, sender=Booking)
def notify_booking_status_change(sender, instance, created, **kwargs):
    """
    Отправляет уведомления при создании, подтверждении или отмене брони.
    """
    if created:
        event = "created"
        status_display = "создана"
    else:
        # Проверяем текущий статус
        if instance.status == 'CONFIRMED':
            event = "confirmed"
            status_display = "подтверждена"
        elif instance.status == 'CANCELED':
            event = "cancelled"
            status_display = "отменена"
        else:
            return

    # --- Уведомление пользователю ---
    try:
        chat = TelegramChat.objects.get(user=instance.user)
        user_message = (
            f"🛖 Бронь {status_display}!\n"
            f"Домик: {instance.accommodation.title}\n"
            f"Даты: {instance.check_in.strftime('%d.%m.%Y')} — {instance.check_out.strftime('%d.%m.%Y')}\n"
            f"Гости: {instance.guests_count}"
        )
        send_telegram_message(chat.chat_id, user_message)
    except TelegramChat.DoesNotExist:
        pass  # пользователь не привязал Telegram

    # --- Уведомление администратору ---
    admin_chat_id = getattr(settings, 'ADMIN_CHAT_ID', None)
    if admin_chat_id:
        admin_message = (
            f"👤 Событие с бронированием!\n"
            f"Пользователь: {instance.user.phone}\n"
            f"Домик: {instance.accommodation.title}\n"
            f"Статус: {status_display}\n"
            f"Даты: {instance.check_in} — {instance.check_out}"
        )
        send_telegram_message(admin_chat_id, admin_message)