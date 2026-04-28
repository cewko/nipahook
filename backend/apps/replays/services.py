import uuid
from dataclasses import dataclass

from django.contrib.auth.models import AnonymousUser
from django.db import transaction

from apps.deliveries.tasks import deliver_webhook
from apps.webhooks.models import WebhookEvent
from .models import EventReplay
from .exceptions import NotReplayableError


class ReplayWebhookEventService:
    replayable_statuses = {
        WebhookEvent.Status.FAILED,
        WebhookEvent.Status.CANCELLED
    }

    @transaction.atomic
    def replay(
        self,
        *,
        event_id: str,
        actor=None,
        reason: str = ""
    ) -> EventReplay:
        original_event = (
            WebhookEvent.objects
            .select_for_update()
            .select_related("destination")
            .get(id=event_id)
        )

        if original_event.status not in self.replayable_statuses:
            raise NotReplayableError(
                f"Event with status '{original_event.status}' cannot be replayed"
            )

        replay_event = WebhookEvent.objects.create(
            destination=original_event.destination,
            idempotency_key=self._build_replay_idempotency_key(original_event),
            method=original_event.method,
            headers=original_event.headers,
            query_params=original_event.query_params,
            payload=original_event.payload,
            payload_hash=original_event.payload_hash,
            status=WebhookEvent.Status.QUEUED,
        )

        replay = EventReplay.objects.create(
            original_event=original_event,
            replay_event=replay_event,
            requested_by=self._get_actor(actor),
            reason=reason,
            metadata={
                "original_status": original_event.status,
                "original_idempotency_key": original_event.idempotency_key,
                "destination_id": str(original_event.destination)
            }
        )

        transaction.on_commit(
            lambda: deliver_webhook.delay(str(replay_event.id))
        )

        return replay

    def _build_replay_idempotency_key(self, event: WebhookEvent) -> str:
        return f"replay:{event.id}:{uuid.uuid4()}"

    def _get_actor(self, actor):
        if actor is None or isinstance(actor, AnonymousUser):
            return None

        if not getattr(actor, "is_authenticated", False):
            return None

        return actor


