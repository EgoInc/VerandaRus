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
