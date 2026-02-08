import uuid
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from .houses import Accommodation


class Booking(models.Model):
    """Booking for an accommodation unit."""

    class Status(models.TextChoices):
        # Booking is created, waiting for confirmation.
        NEW = "NEW", "New"
        # Booking is confirmed.
        CONFIRMED = "CONFIRMED", "Confirmed"
        # Booking is canceled.
        CANCELED = "CANCELED", "Canceled"
        # Booking is completed.
        COMPLETED = "COMPLETED", "Completed"

    # Primary key as UUID for safer public exposure.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Accommodation being booked.
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name="bookings")
    # User who made the booking.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    # Check-in date (inclusive).
    check_in = models.DateField()
    # Check-out date (exclusive).
    check_out = models.DateField()
    # Guests count for this booking.
    guests_count = models.PositiveSmallIntegerField(default=1)
    # Booking status.
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    # Total booking price.
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    # Optional guest comment.
    comment = models.CharField(max_length=512, blank=True)
    # Timestamp when the record was created.
    created_at = models.DateTimeField(auto_now_add=True)
    # Timestamp when the record was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        indexes = [
            models.Index(fields=["accommodation", "check_in", "check_out"], name="idx_booking_dates"),
            models.Index(fields=["user", "created_at"], name="idx_booking_user_created"),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_in__lt=models.F("check_out")),
                name="booking_check_in_before_check_out",
            ),
        ]

    def clean(self):
        """Validate that dates are in correct order."""
        if self.check_in and self.check_out and self.check_in >= self.check_out:
            raise ValidationError("check_in must be earlier than check_out.")

    def __str__(self):
        return f"{self.accommodation} {self.check_in} - {self.check_out}"
