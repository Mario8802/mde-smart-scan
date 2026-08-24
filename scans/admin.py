from django.contrib import admin

from .models import AuditEvent, ScanRecord


@admin.register(ScanRecord)
class ScanRecordAdmin(admin.ModelAdmin):
    list_display = (
        "tracking_number",
        "item_type",
        "recipient_name",
        "status",
        "confidence",
        "created_at",
    )
    list_filter = ("item_type", "status", "source")
    search_fields = ("tracking_number", "recipient_name", "street", "city")
    readonly_fields = ("created_at", "confirmed_at", "printed_at")


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("scan", "action", "actor_label", "created_at")
    list_filter = ("action",)
    readonly_fields = ("created_at",)
