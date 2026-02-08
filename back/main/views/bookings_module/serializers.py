from rest_framework import serializers
from main.models import Booking


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "accommodation",
            "check_in",
            "check_out",
            "guests_count",
        ]


class BookingListSerializer(serializers.ModelSerializer):
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
