import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user for phone-based auth in the future."""

    # Phone number used for SMS login (nullable for legacy / dev flow).
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class BlacklistedPhone(models.Model):
    """Phones blocked from booking or registration."""

    # Primary key as UUID for safer public exposure.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Phone number that is blocked.
    phone = models.CharField(max_length=20, unique=True)
    # Optional reason for the blacklist entry.
    reason = models.CharField(max_length=255, blank=True)
    # Timestamp when the record was created.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Blacklisted phone"
        verbose_name_plural = "Blacklisted phones"

    def __str__(self):
        return self.phone
