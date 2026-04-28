from rest_framework import status, mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.audit.models import AuditLog
from apps.audit.services import create_audit_log
from apps.webhooks.models import WebhookEvent

from .models import EventReplay
from .serializers import EventReplaySerializer, EventReplayCreateSerializer
from .services import ReplayWebhookEventService
from .exceptions import NotReplayableError


class EventReplayViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    serializer_class = EventReplaySerializer
    lookup_field = "id"

    def get_serializer_class(self):
        if self.action == "create":
            return EventReplayCreateSerializer

        return self.serializer_class

    def get_queryset(self):
        queryset = (
            EventReplay.objects
            .select_related("original_event", "replay_event", "requested_by")
        )

        original_event_id = self.request.query_params.get("original_event")
        if original_event_id:
            queryset = queryset.filter(original_event__id=original_event_id)
        
        replay_event_id = self.request.query_params.get("replay_event_id")
        if replay_event_id:
            queryset = queryset.filter(replay_event__id=replay_event_id)

        return queryset

    def create(self, request):
        serializer = EventReplayCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ReplayWebhookEventService()

        try:
            replay = service.replay(
                event_id=str(serializer.validated_data["event_id"]),
                actor=request.user,
                reason=serializer.validated_data.get("reason", "")
            )
        except WebhookEvent.DoesNotExist:
            return Response({
                "detail": "Webhook event not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except NotReplayableError as _e:
            return Response({
                "detail": str(_e)
            }, status=status.HTTP_409_CONFLICT)

        create_audit_log(
            action=AuditLog.Action.EVENT_REPLAYED,
            actor=request.user,
            entity=replay.replay_event,
            request=request,
            metadata={
                "replay_id": str(replay.id),
                "original_event_id": str(replay.original_event.id),
                "replay_event_id": str(replay.replay_event.id),
                "reason": replay.reason
            }
        )

        response_serializer = EventReplaySerializer(replay)
        return Response(response_serializer.data, status=status.HTTP_202_ACCEPTED)