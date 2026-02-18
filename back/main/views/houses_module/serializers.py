from rest_framework import serializers
from main.models import Accommodation


class AccommodationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accommodation
        fields = [
            "id",
            "title",
            "description",
            "area_m2",
            "capacity_min",
            "capacity_max",
            "is_active",
        ]


class DayAvailabilitySerializer(serializers.Serializer):
    """A single calendar day's availability and price."""

    date = serializers.DateField()
    is_available = serializers.BooleanField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)


class AvailabilityResponseSerializer(serializers.Serializer):
    """Full availability response for an accommodation."""

    accommodation_id = serializers.UUIDField()
    date_from = serializers.DateField()
    date_to = serializers.DateField()
    days = DayAvailabilitySerializer(many=True)


class AvailabilityQuerySerializer(serializers.Serializer):
    """Query params for the availability endpoint."""

    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
