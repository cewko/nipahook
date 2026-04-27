from django.db import models
from apps.common.models import UUIDModel, TimeStampedModel


class DeliveryAttempt(UUIDModel, TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    event = models.ForeignKey(
        "webhooks.WebhookEvent",
        on_delete=models.CASCADE,
        related_name="delivery_attempts"
    )
    destination = models.ForeignKey(
        "destinations.Destination",
        on_delete=models.PROTECT,
        related_name="delivery_attempts",
    )

    attempt_number = models.PositiveSmallIntegerField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )

    request_url = models.URLField(max_length=2048)
    request_headers = models.JSONField(default=dict)
    request_body = models.JSONField(default=dict)

    response_status_code = models.PositiveSmallIntegerField(null=True, blank=True)
    response_headers = models.JSONField(default=dict)
    response_body = models.TextField(blank=True)

    error_message = models.TextField(blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)

    scheduled_at = models.DateTimeField()
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event", "attempt_number"]),
            models.Index(fields=["destination", "status", "-created_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["event", "attempt_number"],
                name="unique_attempt_number_per_event",
            )
        ]

    def __str__(self):
        return f"{self.event_id} attempt {self.attempt_number} - {self.status}"
