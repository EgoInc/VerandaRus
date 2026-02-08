from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import (
    User,
    BlacklistedPhone,
    Accommodation,
    Amenity,
    AccommodationAmenity,
    AccommodationImage,
    PriceRule,
    Booking,
)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Admin configuration for custom User model."""

    # Columns for the user list.
    list_display = ("id", "username", "email", "phone", "is_staff", "is_active")
    # Search by username, email, or phone.
    search_fields = ("username", "email", "phone")


@admin.register(BlacklistedPhone)
class BlacklistedPhoneAdmin(admin.ModelAdmin):
    """Admin configuration for blacklisted phones."""

    list_display = ("id", "phone", "reason", "created_at")
    search_fields = ("phone", "reason")


@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    """Admin configuration for accommodations."""

    list_display = ("id", "title", "type", "capacity_min", "capacity_max", "is_active", "created_at")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    """Admin configuration for amenities."""

    list_display = ("id", "name", "icon")
    search_fields = ("name",)


@admin.register(AccommodationAmenity)
class AccommodationAmenityAdmin(admin.ModelAdmin):
    """Admin configuration for accommodation-amenity links."""

    list_display = ("id", "accommodation", "amenity")
    search_fields = ("accommodation__title", "amenity__name")


@admin.register(AccommodationImage)
class AccommodationImageAdmin(admin.ModelAdmin):
    """Admin configuration for accommodation images."""

    list_display = ("id", "accommodation", "order", "created_at")
    search_fields = ("accommodation__title",)


@admin.register(PriceRule)
class PriceRuleAdmin(admin.ModelAdmin):
    """Admin configuration for price rules."""

    list_display = ("id", "accommodation", "kind", "price_per_night", "priority", "is_active")
    search_fields = ("accommodation__title",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin configuration for bookings."""

    list_display = ("id", "accommodation", "user", "check_in", "check_out", "status", "total_price")
    search_fields = ("accommodation__title", "user__username", "user__email")
