from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import DeliveryAttempt
from .serializers import DeliveryAttemptSerializer


class DeliveryAttemptViewSet(ReadOnlyModelViewSet):
    serializer_class = DeliveryAttemptSerializer
    lookup_field = "id"

    def get_queryset(self):
        queryset = DeliveryAttempt.objects.select_related("event", "destination")

        event_id = self.request.query_params.get("event")
        if event_id:
            queryset = queryset.filter(event__id=event_id)

        return queryset