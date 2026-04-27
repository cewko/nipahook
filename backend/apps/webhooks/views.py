from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.destinations.models import Destination
from .serializers import IngestWebhookResponseSerializer
from .exceptions import DestinationInactiveError
from .services import (
    IngestWebhookRequest,
    IngestWebhookService,
)


class WebhookIngestView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, destination_id):
        service = IngestWebhookService()

        raw_body = request.body
        payload = request.data

        try:
            result = service.ingest(
                IngestWebhookRequest(
                    destination_id=destination_id,
                    method=request.method,
                    headers=dict(request.headers),
                    query_params=request.query_params.dict(),
                    payload=payload,
                    raw_body=raw_body,
                )
            )
        except Destination.DoesNotExist:
            return Response(
                {"detail": "Destination not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except DestinationInactiveError:
            return Response(
                {"detail": "Destination is disabled."},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = IngestWebhookResponseSerializer(result)
        response_status = (
            status.HTTP_202_ACCEPTED
            if result.created
            else status.HTTP_200_OK
        )

        return Response(serializer.data, status=response_status)