import hashlib

from django.db import models
from django.utils import timezone

from apps.common.models import UUIDModel, TimeStampedModel
from apps.destinations.models import Destination


class WebhookEvent(UUIDModel, TimeStampedModel):
    class Status(models.TextChoices):
        RECEIVED = "received", "Received"
        QUEUED = "queued", "Queued"
        DELIVERING = "delivering", "Delivering"
        SUCCESS = "success", "Success"
        RETRYING = "retrying", "Retrying"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    destination = models.ForeignKey(
        Destination,
        on_delete=models.PROTECT,
        related_name="webhook_events"
    )

    idempotency_key = models.CharField(
        max_length=255,
        blank=True,
        db_index=True
    )

    method = models.CharField(max_length=10)
    headers = models.JSONField(default=dict)
    query_params = models.JSONField(default=dict)
    payload = models.JSONField(default=dict)
    payload_hash = models.CharField(max_length=64, db_index=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RECEIVED,
        db_index=True,
    )

    received_at = models.DateTimeField(default=timezone.now)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Webhook Event"
        verbose_name_plural = "Webhook Events"
        ordering = ["-received_at"]
        indexes = [
            models.Index(fields=["destination", "status", "-received_at"]),
            models.Index(fields=["payload_hash"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["destination", "idempotency_key"],
                condition=~models.Q(idempotency_key=""),
                name="unique_idempotency_key_per_destination"
            )
        ]

    def __str__(self):
        return f"{self.destination.name} - {self.status}"

    @staticmethod
    def build_payload_hash(raw_body: bytes) -> str:
        return hashlib.sha256(raw_body).hexdigest()