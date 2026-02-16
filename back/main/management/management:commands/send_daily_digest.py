from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from main.models.bookings import Booking
from main.models.telegram import TelegramChat
from main.views.telegram_module.bot import send_telegram_message


class Command(BaseCommand):
    help = 'Отправляет ежедневный дайджест администратору и напоминания пользователям о завтрашнем заезде'

    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-only',
            action='store_true',
            help='Отправить только администратору (без пользовательских напоминаний)',
        )

    def handle(self, *args, **options):
        tomorrow = timezone.now().date() + timedelta(days=1)

        # --- Дайджест для администратора ---
        admin_chat_id = getattr(settings, 'ADMIN_CHAT_ID', None)
        if admin_chat_id:
            bookings = Booking.objects.filter(
                check_in__date=tomorrow,
                status__in=['CONFIRMED']
            )
            if bookings.exists():
                houses = bookings.values_list('accommodation__title', flat=True).distinct()
                message = f"🏠 Завтра заняты: {', '.join(houses)}"
                send_telegram_message(admin_chat_id, message)
                self.stdout.write(self.style.SUCCESS('Дайджест администратору отправлен'))
            else:
                self.stdout.write('Нет броней на завтра, дайджест не отправлен')
        else:
            self.stdout.write(self.style.WARNING('ADMIN_CHAT_ID не настроен'))

        # --- Напоминания пользователям о завтрашнем заезде (если не указано --admin-only) ---
        if not options['admin_only']:
            upcoming_bookings = Booking.objects.filter(
                check_in__date=tomorrow,
                status__in=['CONFIRMED']
            ).select_related('user', 'accommodation')

            count = 0
            for booking in upcoming_bookings:
                try:
                    chat = TelegramChat.objects.get(user=booking.user)
                    message = (
                        f"🔔 Напоминание: завтра заезд!\n"
                        f"Домик: {booking.accommodation.title}\n"
                        f"Даты: {booking.check_in.strftime('%d.%m.%Y')} — {booking.check_out.strftime('%d.%m.%Y')}\n"
                        f"Гости: {booking.guests_count}"
                    )
                    send_telegram_message(chat.chat_id, message)
                    count += 1
                except TelegramChat.DoesNotExist:
                    continue

            self.stdout.write(self.style.SUCCESS(f'Напоминаний отправлено пользователям: {count}'))