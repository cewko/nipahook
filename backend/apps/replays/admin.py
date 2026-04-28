from django.contrib import admin
from .models import EventReplay


@admin.register(EventReplay)
class EventReplayAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "original_event",
        "replay_event",
        "requested_by",
        "created_at",
    ]

    list_filter = [
        "created_at",
    ]

    search_fields = [
        "id",
        "original_event__id",
        "replay_event__id",
        "requested_by__username",
        "requested_by__email",
    ]

    readonly_fields = [
        "pkid",
        "id",
        "original_event",
        "replay_event",
        "requested_by",
        "reason",
        "metadata",
        "created_at",
        "updated_at",
    ]

    ordering = ["-created_at"]

    def has_add_permission(self, request):
        return False
