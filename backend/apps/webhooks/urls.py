from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import WebhookIngestView, WebhookEventViewSet


router = DefaultRouter()
router.register("webhooks", WebhookEventViewSet, basename="webhook")

urlpatterns = [
    path(
        "ingest/<uuid:destination_id>/",
        WebhookIngestView.as_view(),
        name="webhook-ingest",
    ),
]

urlpatterns += router.urls