"""
Admin site configuration for Corp Inventory
"""

from django.contrib import admin
from .models import (
    Corporation,
    HangarDivision,
    Location,
    HangarItem,
    HangarTransaction,
    HangarSnapshot,
    AlertRule,
)


@admin.register(Corporation)
class CorporationAdmin(admin.ModelAdmin):
    list_display = (
        "corporation_name",
        "corporation_id",
        "tracking_enabled",
        "last_sync",
        "created_at",
    )
    list_filter = ("tracking_enabled", "last_sync")
    search_fields = ("corporation_name", "corporation_id")
    readonly_fields = ("last_sync", "last_update", "created_at")
    actions = ["enable_tracking", "disable_tracking"]
    
    def enable_tracking(self, request, queryset):
        queryset.update(tracking_enabled=True)
        self.message_user(request, f"Enabled tracking for {queryset.count()} corporations")
    enable_tracking.short_description = "Enable hangar tracking"
    
    def disable_tracking(self, request, queryset):
        queryset.update(tracking_enabled=False)
        self.message_user(request, f"Disabled tracking for {queryset.count()} corporations")
    disable_tracking.short_description = "Disable hangar tracking"


@admin.register(HangarDivision)
class HangarDivisionAdmin(admin.ModelAdmin):
    list_display = ("corporation", "division_id", "division_name")
    list_filter = ("corporation",)
    search_fields = ("division_name", "corporation__corporation_name")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        "location_name",
        "location_id",
        "location_type",
        "solar_system_name",
        "region_name",
    )
    list_filter = ("location_type", "region_name")
    search_fields = ("location_name", "solar_system_name", "region_name")
    readonly_fields = ("last_update",)


@admin.register(HangarItem)
class HangarItemAdmin(admin.ModelAdmin):
    list_display = (
        "type_name",
        "quantity",
        "corporation",
        "location",
        "division",
        "estimated_value",
        "is_active",
        "last_seen",
    )
    list_filter = ("corporation", "is_active", "division", "location")
    search_fields = ("type_name", "item_id")
    readonly_fields = ("first_seen", "last_seen", "item_id")
    date_hierarchy = "last_seen"


@admin.register(HangarTransaction)
class HangarTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "detected_at",
        "transaction_type",
        "type_name",
        "quantity_change",
        "character_name",
        "corporation",
        "location",
        "estimated_value",
    )
    list_filter = (
        "transaction_type",
        "corporation",
        "detected_at",
        "notification_sent",
    )
    search_fields = (
        "type_name",
        "character_name",
        "corporation__corporation_name",
    )
    readonly_fields = ("detected_at",)
    date_hierarchy = "detected_at"


@admin.register(HangarSnapshot)
class HangarSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        "corporation",
        "snapshot_time",
        "total_items",
        "total_value",
    )
    list_filter = ("corporation", "snapshot_time")
    readonly_fields = ("snapshot_time", "snapshot_data")
    date_hierarchy = "snapshot_time"


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "corporation",
        "alert_type",
        "type_name",
        "is_active",
        "created_at",
    )
    list_filter = ("alert_type", "is_active", "corporation")
    search_fields = ("name", "type_name", "corporation__corporation_name")
    filter_horizontal = ("notify_users",)
    readonly_fields = ("created_at",)
