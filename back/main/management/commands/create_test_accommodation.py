from decimal import Decimal

from django.core.management.base import BaseCommand

from main.models import Accommodation, PriceRule


SLUG = "test-house-1"


class Command(BaseCommand):
    help = "Создание тестового объека для бронирования"

    def handle(self, *args, **options):
        accommodation, created = Accommodation.objects.get_or_create(
            slug=SLUG,
            defaults={
                "title": "Тестовый домик №1",
                "type": Accommodation.AccommodationType.HOUSE,
                "description": "Тестовый объект для проверки бронирования.",
                "area_m2": 60,
                "capacity_min": 1,
                "capacity_max": 6,
                "is_active": True,
            },
        )

        if not created:
            self.stdout.write(
                self.style.NOTICE(f"Объект '{SLUG}' уже создан (id={accommodation.pk}).")
            )
        else:
            self.stdout.write(self.style.SUCCESS(f"Создан объект '{SLUG}' (id={accommodation.pk})."))

        rules = [
            dict(
                kind=PriceRule.Kind.WEEKDAY,
                price_per_night=Decimal("5000.00"),
                priority=1,
            ),
            dict(
                kind=PriceRule.Kind.WEEKEND,
                price_per_night=Decimal("7500.00"),
                priority=1,
            ),
        ]

        for rule_data in rules:
            _, rule_created = PriceRule.objects.get_or_create(
                accommodation=accommodation,
                kind=rule_data["kind"],
                date_from=None,
                date_to=None,
                defaults={
                    "price_per_night": rule_data["price_per_night"],
                    "priority": rule_data["priority"],
                    "is_active": True,
                },
            )
            label = rule_data["kind"]
            price = rule_data["price_per_night"]
            if rule_created:
                self.stdout.write(self.style.SUCCESS(f"  + Цена '{label}': {price} ₽/ночь"))
            else:
                self.stdout.write(self.style.NOTICE(f"  ~ Цена '{label}' уже установлена."))

        self.stdout.write("")
        self.stdout.write("Новый объект создан! ID объекта:")
        self.stdout.write(self.style.SUCCESS(f"  {accommodation.pk}"))
