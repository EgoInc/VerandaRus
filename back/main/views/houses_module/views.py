from datetime import date, timedelta

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from main.models import Accommodation, Booking
from main.utils.pricing import get_prices_for_range

from .serializers import (
    AccommodationSerializer,
    AvailabilityQuerySerializer,
    AvailabilityResponseSerializer,
    DayAvailabilitySerializer,
)


class HousesListView(APIView):
    """List all active accommodations."""

    serializer_class = AccommodationSerializer

    @extend_schema(
        summary="Вывести доступные объекты для брони",
        responses=AccommodationSerializer(many=True),
        tags=["accommodations"],
        operation_id="accommodations_list",
    )
    def get(self, request):
        qs = Accommodation.objects.filter(is_active=True)
        serializer = AccommodationSerializer(qs, many=True)
        return Response(serializer.data)


# Statuses that block a calendar date.
_BLOCKING_STATUSES = {Booking.Status.NEW, Booking.Status.CONFIRMED}

# Default window (days) when no date range is provided.
_DEFAULT_WINDOW_DAYS = 30


class AccommodationAvailabilityView(APIView):
    """Return a day-by-day availability calendar with prices for an accommodation."""

    @extend_schema(
        summary="Информация о доступности объекта",
        description=(
            f"Возвращает информацию о доступности объекта в выбранный период (по дефолту {_DEFAULT_WINDOW_DAYS} дней). "
            "Объект недоступен, если в день есть бронь с NEW или CONFIRMED. "
        ),
        parameters=[
            OpenApiParameter(
                name="date_from",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Начало диапазона периода (по дефолту - сегодня)",
                required=False,
            ),
            OpenApiParameter(
                name="date_to",
                type=str,
                location=OpenApiParameter.QUERY,
                description=f"Конец диапазона периода. По дефолту date_from + {_DEFAULT_WINDOW_DAYS} days.",
                required=False,
            ),
        ],
        responses={
            200: AvailabilityResponseSerializer,
            400: None,
            404: None,
        },
        tags=["accommodations"],
        operation_id="accommodations_availability",
    )
    def get(self, request, pk):
        try:
            accommodation = Accommodation.objects.get(pk=pk, is_active=True)
        except Accommodation.DoesNotExist:
            return Response(
                {"detail": "Accommodation not found or inactive."},
                status=status.HTTP_404_NOT_FOUND,
            )

        q = AvailabilityQuerySerializer(data=request.query_params)
        if not q.is_valid():
            return Response(q.errors, status=status.HTTP_400_BAD_REQUEST)

        today = date.today()
        date_from: date = q.validated_data.get("date_from") or today
        date_to: date = q.validated_data.get("date_to") or (
            date_from + timedelta(days=_DEFAULT_WINDOW_DAYS)
        )

        if date_from >= date_to:
            return Response(
                {"detail": "date_from must be earlier than date_to."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        blocking_bookings = Booking.objects.filter(
            accommodation=accommodation,
            status__in=_BLOCKING_STATUSES,
            check_in__lt=date_to,
            check_out__gt=date_from,
        ).values_list("check_in", "check_out")

        booked_dates: set[date] = set()
        for check_in, check_out in blocking_bookings:
            d = check_in
            while d < check_out:
                if date_from <= d < date_to:
                    booked_dates.add(d)
                d += timedelta(days=1)

        prices = get_prices_for_range(accommodation, date_from, date_to)

        days = []
        d = date_from
        while d < date_to:
            days.append(
                {
                    "date": d,
                    "is_available": d not in booked_dates,
                    "price": prices.get(d),
                }
            )
            d += timedelta(days=1)

        payload = {
            "accommodation_id": accommodation.pk,
            "date_from": date_from,
            "date_to": date_to,
            "days": days,
        }
        serializer = AvailabilityResponseSerializer(payload)
        return Response(serializer.data)
