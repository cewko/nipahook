from rest_framework import serializers
from apps.webhooks.models import WebhookEvent
from .models import EventReplay


class EventReplaySerializer(serializers.ModelSerializer):
    original_event = serializers.UUIDField(source="original_event.id", read_only=True)
    replay_event = serializers.UUIDField(source="replay_event.id", read_only=True)
    requested_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = EventReplay
        fields = [
            "id",
            "original_event",
            "replay_event",
            "requested_by",
            "reason",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class EventReplayCreateSerializer(serializers.Serializer):
    event_id = serializers.UUIDField()
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=1000
    )

    def validate_event_id(self, value):
        if not WebhookEvent.objects.filter(id=value).exists():
            raise serializers.ValidationError("Event with this ID not found")

        return value