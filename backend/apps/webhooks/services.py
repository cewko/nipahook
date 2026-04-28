from dataclasses import dataclass

from django.db import transaction

from apps.destinations.models import Destination
from apps.deliveries.tasks import deliver_webhook
from .models import WebhookEvent
from .exceptions import DestinationInactiveError, WebhookNotCancellableError


@dataclass(frozen=True)
class CancelWebhookResult:
    event: WebhookEvent
    previous_status: str


class WebhookCancellationService:
    cancellable_statuses = {
        WebhookEvent.Status.RECEIVED,
        WebhookEvent.Status.QUEUED,
        WebhookEvent.Status.RETRYING,
        WebhookEvent.Status.FAILED,
    }

    @transaction.atomic
    def cancel(self, event_id: str) -> CancelWebhookResult:
        event = (
            WebhookEvent.objects
            .select_for_update()
            .select_related("destination")
            .get(id=event_id)
        )

        previous_status = event.status

        if event.status == WebhookEvent.Status.CANCELLED:
            return CancelWebhookResult(event=event, previous_status=previous_status)

        if event.status not in self.cancellable_statuses:
            raise WebhookNotCancellableError(
                f"Event with status '{event.status}' cannot be cancelled")

        event.status = WebhookEvent.Status.CANCELLED
        event.next_retry_at = None
        event.failed_at = None
        event.save(update_fields=[
            "status",
            "next_retry_at",
            "failed_at",
            "updated_at"
        ])

        return CancelWebhookResult(event=event, previous_status=previous_status)


@dataclass(frozen=True)
class IngestWebhookResult:
    event: WebhookEvent
    created: bool


@dataclass(frozen=True)
class IngestWebhookRequest:
    destination_id: str
    method: str
    headers: dict
    query_params: dict
    payload: dict
    raw_body: bytes


class IngestWebhookService:
    def ingest(self, data: IngestWebhookRequest) -> IngestWebhookResult:
        destination = self._get_active_destination(data.destination_id)
        idempotency_key = self._extract_idempotency_key(data.headers, data.payload)
    
        with transaction.atomic():
            existing_event = self._get_existing_event(destination, idempotency_key)

            if existing_event:
                return IngestWebhookResult(
                    event=existing_event,
                    created=False
                )

            event = WebhookEvent.objects.create(
                destination=destination,
                idempotency_key=idempotency_key,
                method=data.method,
                headers=data.headers,
                query_params=data.query_params,
                payload=data.payload,
                payload_hash=WebhookEvent.build_payload_hash(data.raw_body),
                status=WebhookEvent.Status.QUEUED,
            )

            transaction.on_commit(
                lambda: deliver_webhook.delay(str(event.id))
            )

            return IngestWebhookResult(
                event=event,
                created=True
            )

    def _get_active_destination(self, destination_id: str) -> Destination:
        destination = Destination.objects.get(id=destination_id)

        if destination.status != Destination.Status.ACTIVE:
            raise DestinationInactiveError("Destination is disabled")

        return destination

    def _extract_idempotency_key(self, headers: dict, payload: dict) -> str:
        return (
            headers.get("Idempotency-Key")
            or headers.get("X-Idempotency-Key")
            or headers.get("X-Webhook-Id")
            or headers.get("X-Event-Id")
            or payload.get("id")
            or payload.get("event_id")
            or ""
        )

    def _get_existing_event(
        self,
        destination: Destination,
        idempotency_key: str,
    ) -> WebhookEvent | None:
        if not idempotency_key:
            return None

        return (
            WebhookEvent.objects
            .filter(
                destination=destination,
                idempotency_key=idempotency_key
            )
            .first()
        )