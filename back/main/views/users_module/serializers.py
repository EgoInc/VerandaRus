from rest_framework import serializers
from main.models import BlacklistedPhone, Booking


class BlacklistedPhoneSerializer(serializers.ModelSerializer):
    """Serializer for adding phone to blacklist."""

    class Meta:
        model = BlacklistedPhone
        fields = ["id", "phone", "reason", "created_at"]
        read_only_fields = ["id", "created_at"]


class MyBookingSerializer(serializers.ModelSerializer):
    """Serializer for listing current user bookings."""

    class Meta:
        model = Booking
        fields = [
            "id",
            "accommodation",
            "check_in",
            "check_out",
            "guests_count",
            "status",
            "total_price",
        ]


class DevLoginSerializer(serializers.Serializer):
    """Input serializer for dev-only login by username."""

    # Any username or phone-like string; used as username for dev user.
    login = serializers.CharField()
    # Any password value is accepted in dev mode.
    password = serializers.CharField()


class DevLoginResponseSerializer(serializers.Serializer):
    """Output serializer for dev-only login response."""

    # Token for authenticated requests.
    token = serializers.CharField()
    # User ID in the system.
    user_id = serializers.IntegerField()
    # Username used for dev user.
    username = serializers.CharField()


class AuthorizationSerializer(serializers.Serializer):
    """Input serializer for phone-based authorization (password ignored for now)."""

    phone = serializers.CharField()
    password = serializers.CharField()


class AuthorizationResponseSerializer(serializers.Serializer):
    """Output serializer for phone-based authorization."""

    access = serializers.CharField()
    refresh = serializers.CharField()
    user_id = serializers.IntegerField()
    phone = serializers.CharField()
