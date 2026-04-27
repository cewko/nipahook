from rest_framework import serializers
from .models import DeliveryAttempt


class DeliveryAttemptSerializer(serializers.ModelSerializer):
    event = serializers.UUIDField(source="event.id", read_only=True)
    destination = serializers.UUIDField(source="destination.id", read_only=True)

    class Meta:
        model = DeliveryAttempt
        fields = [
            "id",
            "event",
            "destination",
            "attempt_number",
            "status",
            "request_url",
            "request_headers",
            "request_body",
            "response_status_code",
            "response_headers",
            "response_body",
            "error_message",
            "duration_ms",
            "scheduled_at",
            "started_at",
            "finished_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
