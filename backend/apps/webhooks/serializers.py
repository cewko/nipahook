from rest_framework import serializers
from .models import WebhookEvent


class WebhookEventSerializer(serializers.ModelSerializer):
    destination = serializers.UUIDField(source="destination.id", read_only=True)

    class Meta:
        model = WebhookEvent
        fields = [
            "id",
            "destination",
            "idempotency_key",
            "method",
            "headers",
            "query_params",
            "payload",
            "payload_hash",
            "status",
            "received_at",
            "next_retry_at",
            "delivered_at",
            "failed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class IngestWebhookResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEvent
        fields = ["id", "status", "received_at"]
