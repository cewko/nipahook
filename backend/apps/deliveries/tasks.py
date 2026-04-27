from celery import shared_task
from .services import DeliveryService


@shared_task(name="deliveries.deliver_webhook")
def deliver_webhook(event_id: str) -> None:
    DeliveryService().deliver(event_id)