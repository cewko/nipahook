from django.contrib import admin

from .models import WebhookEvent


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "destination",
        "idempotency_key",
        "method",
        "status",
        "received_at",
        "created_at",
    ]

    list_filter = [
        "status",
        "method",
        "received_at",
        "created_at",
    ]

    search_fields = [
        "id",
        "idempotency_key",
        "payload_hash",
        "destination__name",
        "destination__target_url",
    ]

    readonly_fields = [
        "pkid",
        "id",
        "destination",
        "idempotency_key",
        "method",
        "headers",
        "query_params",
        "payload",
        "payload_hash",
        "received_at",
        "next_retry_at",
        "delivered_at",
        "failed_at",
        "created_at",
        "updated_at",
    ]

    ordering = ["-received_at"]

    fieldsets = [
        (
            "Event",
            {
                "fields": [
                    "pkid",
                    "id",
                    "destination",
                    "idempotency_key",
                    "status",
                ]
            },
        ),
        (
            "Request",
            {
                "fields": [
                    "method",
                    "headers",
                    "query_params",
                    "payload",
                    "payload_hash",
                ]
            },
        ),
        (
            "Timestamps",
            {
                "fields": [
                    "received_at",
                    "next_retry_at",
                    "delivered_at",
                    "failed_at",
                    "created_at",
                    "updated_at",
                ]
            },
        ),
    ]

    def has_add_permission(self, request):
        return False
