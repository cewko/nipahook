from django.urls import path
from .views import WebhookIngestView


urlpatterns = [
    path(
        "ingest/<uuid:destination_id>/",
        WebhookIngestView.as_view(),
        name="webhook-ingest",
    ),
]