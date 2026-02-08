import uuid
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models
from .houses import Accommodation


class PriceRule(models.Model):
    """Pricing rules for accommodations."""

    class Kind(models.TextChoices):
        # Default weekday price.
        WEEKDAY = "WEEKDAY", "Weekday"
        # Default weekend price.
        WEEKEND = "WEEKEND", "Weekend"
        # Custom period price.
        PERIOD = "PERIOD", "Period"

    # Primary key as UUID for safer public exposure.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Linked accommodation.
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name="price_rules")
    # Rule kind (weekday, weekend, or specific period).
    kind = models.CharField(max_length=20, choices=Kind.choices)
    # Price per night for this rule.
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    # Period start date (required for PERIOD).
    date_from = models.DateField(null=True, blank=True)
    # Period end date (required for PERIOD).
    date_to = models.DateField(null=True, blank=True)
    # Priority for rule selection (higher wins).
    priority = models.PositiveSmallIntegerField(default=0)
    # Active flag to enable/disable rule.
    is_active = models.BooleanField(default=True)
    # Timestamp when the record was created.
    created_at = models.DateTimeField(auto_now_add=True)
    # Timestamp when the record was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Price rule"
        verbose_name_plural = "Price rules"
        indexes = [
            models.Index(fields=["accommodation", "kind", "is_active"], name="idx_price_rule_kind"),
            models.Index(fields=["accommodation", "date_from", "date_to"], name="idx_price_rule_dates"),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(kind="PERIOD", date_from__isnull=False, date_to__isnull=False)
                    | models.Q(kind__in=["WEEKDAY", "WEEKEND"], date_from__isnull=True, date_to__isnull=True)
                ),
                name="price_rule_dates_by_kind",
            ),
            models.CheckConstraint(
                check=models.Q(date_from__lte=models.F("date_to")) | models.Q(date_from__isnull=True, date_to__isnull=True),
                name="price_rule_valid_range",
            ),
        ]

    def clean(self):
        """Validate date rules based on rule kind."""
        if self.kind == self.Kind.PERIOD:
            if not self.date_from or not self.date_to:
                raise ValidationError("PERIOD rules require date_from and date_to.")
            if self.date_from > self.date_to:
                raise ValidationError("date_from must be less than or equal to date_to.")
        else:
            if self.date_from or self.date_to:
                raise ValidationError("WEEKDAY/WEEKEND rules must not have dates.")

    def __str__(self):
        return f"{self.accommodation} - {self.kind}"
