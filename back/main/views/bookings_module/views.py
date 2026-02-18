from datetime import date

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from main.models import Accommodation, Booking
from main.utils.pricing import calculate_total_price

from .serializers import (
    AdminBookingUpdateSerializer,
    BookingCreateSerializer,
    BookingDetailSerializer,
    BookingListSerializer,
)

_BLOCKING_STATUSES = {Booking.Status.NEW, Booking.Status.CONFIRMED}


def _simulate_payment(booking: Booking) -> None:
    """Simulate a payment - sets status to CONFIRMED."""
    booking.status = Booking.Status.CONFIRMED
    booking.save(update_fields=["status", "updated_at"])


class BookingCreateView(APIView):
    """POST /api/bookings/ - create a booking."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Создать бронирование",
        description=(
            "Создает бронирование для объекта в выбранный период. "
            "Пока что бронирование оплачивается/подтверждается автоматически."
        ),
        request=BookingCreateSerializer,
        responses={
            201: BookingDetailSerializer,
            400: None,
            401: None,
            404: None,
            409: None,
        },
        tags=["bookings"],
        operation_id="bookings_create",
    )
    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        check_in: date = data["check_in"]
        check_out: date = data["check_out"]
        accommodation_id = data["accommodation_id"]

        if check_in >= check_out:
            return Response(
                {"detail": "check_in must be earlier than check_out."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            accommodation = Accommodation.objects.get(
                pk=accommodation_id, is_active=True
            )
        except Accommodation.DoesNotExist:
            return Response(
                {"detail": "Accommodation not found or inactive."},
                status=status.HTTP_404_NOT_FOUND,
            )

        guests_count = data["guests_count"]
        if (
            guests_count < accommodation.capacity_min
            or guests_count > accommodation.capacity_max
        ):
            return Response(
                {
                    "detail": (
                        f"guests_count must be between {accommodation.capacity_min} "
                        f"and {accommodation.capacity_max} for this accommodation."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        conflict_exists = Booking.objects.filter(
            accommodation=accommodation,
            status__in=_BLOCKING_STATUSES,
            check_in__lt=check_out,
            check_out__gt=check_in,
        ).exists()

        if conflict_exists:
            return Response(
                {"detail": "Selected dates are not available for this accommodation."},
                status=status.HTTP_409_CONFLICT,
            )

        try:
            total_price = calculate_total_price(accommodation, check_in, check_out)
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking = Booking.objects.create(
            accommodation=accommodation,
            user=request.user,
            check_in=check_in,
            check_out=check_out,
            guests_count=guests_count,
            comment=data.get("comment", ""),
            total_price=total_price,
            status=Booking.Status.NEW,
        )

        _simulate_payment(booking)

        return Response(
            BookingDetailSerializer(booking).data,
            status=status.HTTP_201_CREATED,
        )


class BookingDetailView(APIView):
    """GET /api/bookings/{id}/ — booking details (owner only)."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Детали брони",
        description="Возвращает информацию о брони. Доступно только пользователю, создавшему бронь.",
        responses={
            200: BookingDetailSerializer,
            401: None,
            403: None,
            404: None,
        },
        tags=["bookings"],
        operation_id="bookings_detail",
    )
    def get(self, request, pk):
        booking = self._get_owner_booking(request, pk)
        if isinstance(booking, Response):
            return booking
        return Response(BookingDetailSerializer(booking).data)

    def _get_owner_booking(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response(
                {"detail": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if booking.user_id != request.user.pk and not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to access this booking."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return booking


class BookingCancelView(APIView):
    """POST /api/bookings/{id}/cancel/ — cancel a booking (owner only)."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Отменить бронирование",
        description=(
            "Отменяет бронирование, если та пользователя или запрос идет от админа. "
        ),
        request=None,
        responses={
            200: BookingDetailSerializer,
            400: None,
            401: None,
            403: None,
            404: None,
        },
        tags=["bookings"],
        operation_id="bookings_cancel",
    )
    def post(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response(
                {"detail": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if booking.user_id != request.user.pk and not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to cancel this booking."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if booking.status not in (Booking.Status.NEW, Booking.Status.CONFIRMED):
            return Response(
                {"detail": f"Cannot cancel a booking with status '{booking.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = Booking.Status.CANCELED
        booking.save(update_fields=["status", "updated_at"])
        return Response(BookingDetailSerializer(booking).data)


class AdminBookingListView(APIView):
    """GET /api/admin/bookings/ — list all bookings (admin only)."""

    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="[Админ] Выводит все бронирования",
        responses={200: BookingListSerializer(many=True)},
        tags=["admin"],
        operation_id="admin_bookings_list",
    )
    def get(self, request):
        bookings = Booking.objects.select_related("accommodation", "user").order_by(
            "-created_at"
        )
        serializer = BookingListSerializer(bookings, many=True)
        return Response(serializer.data)


class AdminBookingUpdateView(APIView):
    """PATCH /api/admin/bookings/{id}/ — update status/comment (admin only)."""

    permission_classes = [IsAdminUser]

    @extend_schema(
        summary="[Админ] Редактировать бронирование",
        description="Изменение информации о бронировании.",
        request=AdminBookingUpdateSerializer,
        responses={
            200: BookingDetailSerializer,
            400: None,
            401: None,
            403: None,
            404: None,
        },
        tags=["admin"],
        operation_id="admin_bookings_update",
    )
    def patch(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response(
                {"detail": "Booking not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AdminBookingUpdateSerializer(
            booking, data=request.data, partial=True
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(BookingDetailSerializer(booking).data)
