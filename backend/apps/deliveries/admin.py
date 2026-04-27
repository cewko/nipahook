from django.contrib import admin
from .models import DeliveryAttempt


@admin.register(DeliveryAttempt)
class DeliveryAttemptAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "event",
        "destination",
        "attempt_number",
        "status",
        "response_status_code",
        "duration_ms",
        "created_at",
    ]

    list_filter = ["status", "response_status_code", "created_at"]

    search_fields = [
        "id",
        "event__id",
        "destination__name",
        "destination__target_url",
    ]

    readonly_fields = [
        "pkid",
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

    def has_add_permission(self, request):
        return False
