from dataclasses import dataclass

from django.db import transaction
from apps.deliveries.services import DeliveryService

from apps.destinations.models import Destination
from .models import WebhookEvent
from .exceptions import DestinationInactiveError


@dataclass(frozen=True)
class IngestWebhookRequest:
    destination_id: str
    method: str
    headers: dict
    query_params: dict
    payload: dict
    raw_body: bytes


class IngestWebhookService:
    def ingest(self, data: IngestWebhookRequest) -> WebhookEvent:
        destination = self._get_active_destination(data.destination_id)
    
        with transaction.atomic():
            event = WebhookEvent.objects.create(
                destination=destination,
                idempotency_key=self._extract_idempotency_key(data.headers, data.payload),
                method=data.method,
                headers=data.headers,
                query_params=data.query_params,
                payload=data.payload,
                payload_hash=WebhookEvent.build_payload_hash(data.raw_body),
                status=WebhookEvent.Status.QUEUED,
            )

            transaction.on_commit(
                lambda: DeliveryService().deliver(str(event.id))
            )

            return event

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