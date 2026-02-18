from rest_framework import serializers
from main.models import Accommodation, Booking


class BookingCreateSerializer(serializers.Serializer):
    """Input: create a new booking."""

    accommodation_id = serializers.UUIDField(
        help_text="UUID of the accommodation to book."
    )
    check_in = serializers.DateField(
        help_text="Check-in date (inclusive). Format: YYYY-MM-DD."
    )
    check_out = serializers.DateField(
        help_text="Check-out date (exclusive). Format: YYYY-MM-DD."
    )
    guests_count = serializers.IntegerField(
        min_value=1,
        default=1,
        help_text="Number of guests.",
    )
    comment = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        max_length=512,
        help_text="Optional guest comment.",
    )


class BookingDetailSerializer(serializers.ModelSerializer):
    """Full booking detail for the owner."""

    accommodation_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "accommodation_id",
            "check_in",
            "check_out",
            "guests_count",
            "status",
            "total_price",
            "comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class BookingListSerializer(serializers.ModelSerializer):
    """Compact booking item for list endpoints."""

    accommodation_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "accommodation_id",
            "check_in",
            "check_out",
            "guests_count",
            "status",
            "total_price",
            "created_at",
        ]
        read_only_fields = fields


class AdminBookingUpdateSerializer(serializers.ModelSerializer):
    """Admin: update booking status / comment."""

    class Meta:
        model = Booking
        fields = ["status", "comment"]
