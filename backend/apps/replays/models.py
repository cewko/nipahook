from django.db import models
from django.conf import settings

from apps.common.models import TimeStampedModel, UUIDModel


class EventReplay(UUIDModel, TimeStampedModel):
    original_event = models.ForeignKey(
        "webhooks.WebhookEvent",
        on_delete=models.PROTECT,
        related_name="replays"
    )
    replay_event = models.OneToOneField(
        "webhooks.WebhookEvent",
        on_delete=models.PROTECT,
        related_name="replay_record"
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="event_replays"
    )

    reason = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["original_event", "-created_at"]),
            models.Index(fields=["replay_event"]),
        ]

    def __str__(self):
        return "Replay {self.id} for {self.original_event.id}"