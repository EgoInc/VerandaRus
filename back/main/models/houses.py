import uuid
from django.db import models


class Accommodation(models.Model):
    """Accommodation unit: house, veranda, gazebo, etc."""

    class AccommodationType(models.TextChoices):
        # Standalone house.
        HOUSE = "HOUSE", "House"
        # Veranda / terrace.
        VERANDA = "VERANDA", "Veranda"
        # Gazebo / pavilion.
        GAZEBO = "GAZEBO", "Gazebo"

    # Primary key as UUID for safer public exposure.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Human-readable title for listings.
    title = models.CharField(max_length=255)
    # URL-friendly unique slug.
    slug = models.SlugField(unique=True)
    # Type of accommodation (house, veranda, gazebo).
    type = models.CharField(max_length=20, choices=AccommodationType.choices, default=AccommodationType.HOUSE)
    # Rich description for the listing.
    description = models.TextField(blank=True)
    # Area in square meters (optional).
    area_m2 = models.PositiveIntegerField(null=True, blank=True)
    # Minimum supported guests count.
    capacity_min = models.PositiveSmallIntegerField(default=1)
    # Maximum supported guests count.
    capacity_max = models.PositiveSmallIntegerField(default=1)
    # Optional base price override (e.g., for fixed nightly price).
    base_price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # Active flag to hide/show in listings.
    is_active = models.BooleanField(default=True)
    # Timestamp when the record was created.
    created_at = models.DateTimeField(auto_now_add=True)
    # Timestamp when the record was last updated.
    updated_at = models.DateTimeField(auto_now=True)
    # Amenities available for this accommodation.
    amenities = models.ManyToManyField("Amenity", through="AccommodationAmenity", related_name="accommodations")

    class Meta:
        verbose_name = "Accommodation"
        verbose_name_plural = "Accommodations"
        ordering = ["title"]

    def __str__(self):
        return self.title


class Amenity(models.Model):
    """Amenity dictionary item (e.g., Wi-Fi, BBQ)."""

    # Primary key as UUID for safer public exposure.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Unique amenity name.
    name = models.CharField(max_length=128, unique=True)
    # Optional icon key for frontend.
    icon = models.CharField(max_length=64, blank=True)

    class Meta:
        verbose_name = "Amenity"
        verbose_name_plural = "Amenities"
        ordering = ["name"]

    def __str__(self):
        return self.name


class AccommodationAmenity(models.Model):
    """Through model for Accommodation <-> Amenity relation."""

    # Primary key as UUID for safer public exposure.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Accommodation instance.
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE)
    # Amenity instance.
    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Accommodation amenity"
        verbose_name_plural = "Accommodation amenities"
        constraints = [
            models.UniqueConstraint(
                fields=["accommodation", "amenity"],
                name="uniq_accommodation_amenity",
            )
        ]

    def __str__(self):
        return f"{self.accommodation} - {self.amenity}"


class AccommodationImage(models.Model):
    """Images attached to an accommodation."""

    # Primary key as UUID for safer public exposure.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Parent accommodation.
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE, related_name="images")
    # Image file.
    image = models.ImageField(upload_to="accommodations/")
    # Order for sorting images in UI.
    order = models.PositiveSmallIntegerField(default=0)
    # Timestamp when the record was created.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Accommodation image"
        verbose_name_plural = "Accommodation images"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.accommodation} image {self.order}"
