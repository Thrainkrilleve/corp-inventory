"""
Models for Corp Inventory
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Corporation(models.Model):
    """
    Represents a corporation being tracked
    """
    corporation_id = models.IntegerField(unique=True, db_index=True)
    corporation_name = models.CharField(max_length=254)
    
    # Tracking enabled
    tracking_enabled = models.BooleanField(default=True)
    
    # Last sync times
    last_sync = models.DateTimeField(null=True, blank=True)
    last_update = models.DateTimeField(auto_now=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Corporation"
        verbose_name_plural = "Corporations"
        default_permissions = ()
        permissions = (
            ("basic_access", "Can access Corp Inventory"),
            ("view_hangar", "Can view corporation hangars"),
            ("view_transactions", "Can view hangar transactions"),
            ("manage_tracking", "Can manage hangar tracking"),
        )
    
    def __str__(self):
        return self.corporation_name


class HangarDivision(models.Model):
    """
    Represents a hangar division within a corporation
    """
    corporation = models.ForeignKey(
        Corporation,
        on_delete=models.CASCADE,
        related_name="divisions"
    )
    division_id = models.IntegerField()
    division_name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = "Hangar Division"
        verbose_name_plural = "Hangar Divisions"
        unique_together = ("corporation", "division_id")
        ordering = ["corporation", "division_id"]
    
    def __str__(self):
        return f"{self.corporation.corporation_name} - {self.division_name}"


class Location(models.Model):
    """
    Represents a location (station/structure) where assets are stored
    """
    location_id = models.BigIntegerField(unique=True, db_index=True)
    location_name = models.CharField(max_length=254)
    location_type = models.CharField(max_length=50)  # station, structure, etc.
    
    # System/Region info
    solar_system_id = models.IntegerField(null=True, blank=True)
    solar_system_name = models.CharField(max_length=100, blank=True)
    region_id = models.IntegerField(null=True, blank=True)
    region_name = models.CharField(max_length=100, blank=True)
    
    # Metadata
    last_update = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"
        ordering = ["location_name"]
    
    def __str__(self):
        return self.location_name


class HangarItem(models.Model):
    """
    Represents an item in a corporation hangar
    """
    corporation = models.ForeignKey(
        Corporation,
        on_delete=models.CASCADE,
        related_name="hangar_items"
    )
    
    # Item identification
    item_id = models.BigIntegerField(unique=True, db_index=True)
    type_id = models.IntegerField(db_index=True)
    type_name = models.CharField(max_length=254)
    
    # Location
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="items"
    )
    
    # Division
    division = models.ForeignKey(
        HangarDivision,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="items"
    )
    
    # Quantity and value
    quantity = models.BigIntegerField(default=1)
    estimated_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        help_text="Estimated ISK value"
    )
    
    # Stack/Container info
    is_singleton = models.BooleanField(default=False)
    is_blueprint_copy = models.BooleanField(default=False)
    
    # Metadata
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        verbose_name = "Hangar Item"
        verbose_name_plural = "Hangar Items"
        ordering = ["-last_seen"]
        indexes = [
            models.Index(fields=["corporation", "is_active"]),
            models.Index(fields=["type_id", "is_active"]),
        ]
    
    def __str__(self):
        return f"{self.type_name} x{self.quantity} @ {self.location.location_name}"


class HangarTransaction(models.Model):
    """
    Represents a transaction (addition or removal) in a hangar
    """
    TRANSACTION_TYPE_CHOICES = (
        ("ADD", "Addition"),
        ("REMOVE", "Removal"),
        ("MOVE", "Movement"),
        ("CHANGE", "Quantity Change"),
    )
    
    corporation = models.ForeignKey(
        Corporation,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    
    # Transaction details
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPE_CHOICES,
        db_index=True
    )
    
    # Item info
    type_id = models.IntegerField(db_index=True)
    type_name = models.CharField(max_length=254)
    
    # Quantity change
    quantity_change = models.BigIntegerField()
    old_quantity = models.BigIntegerField(default=0)
    new_quantity = models.BigIntegerField(default=0)
    
    # Location info
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    division = models.ForeignKey(
        HangarDivision,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Value estimate
    estimated_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0
    )
    
    # Character who made the change (if detectable)
    character_id = models.IntegerField(null=True, blank=True, db_index=True)
    character_name = models.CharField(max_length=254, blank=True)
    
    # Timestamp
    detected_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Notification sent
    notification_sent = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Hangar Transaction"
        verbose_name_plural = "Hangar Transactions"
        ordering = ["-detected_at"]
        indexes = [
            models.Index(fields=["corporation", "-detected_at"]),
            models.Index(fields=["type_id", "-detected_at"]),
            models.Index(fields=["character_id", "-detected_at"]),
        ]
    
    def __str__(self):
        return (
            f"{self.transaction_type}: {self.type_name} "
            f"({self.quantity_change:+d}) @ {self.location.location_name}"
        )


class HangarSnapshot(models.Model):
    """
    Represents a complete snapshot of a corporation's hangar at a point in time
    Used for tracking changes and generating alerts
    """
    corporation = models.ForeignKey(
        Corporation,
        on_delete=models.CASCADE,
        related_name="snapshots"
    )
    
    snapshot_time = models.DateTimeField(auto_now_add=True, db_index=True)
    total_items = models.IntegerField(default=0)
    total_value = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0
    )
    
    # Snapshot data (JSON)
    snapshot_data = models.JSONField(default=dict)
    
    class Meta:
        verbose_name = "Hangar Snapshot"
        verbose_name_plural = "Hangar Snapshots"
        ordering = ["-snapshot_time"]
        indexes = [
            models.Index(fields=["corporation", "-snapshot_time"]),
        ]
    
    def __str__(self):
        return f"{self.corporation.corporation_name} - {self.snapshot_time}"


class AlertRule(models.Model):
    """
    Configure alerts for specific items or conditions
    """
    ALERT_TYPE_CHOICES = (
        ("ITEM_ADDED", "Item Added"),
        ("ITEM_REMOVED", "Item Removed"),
        ("VALUE_THRESHOLD", "Value Threshold Exceeded"),
        ("QUANTITY_CHANGE", "Quantity Changed"),
    )
    
    corporation = models.ForeignKey(
        Corporation,
        on_delete=models.CASCADE,
        related_name="alert_rules"
    )
    
    name = models.CharField(max_length=200)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    
    # Optional: specific type to watch
    type_id = models.IntegerField(null=True, blank=True)
    type_name = models.CharField(max_length=254, blank=True)
    
    # Optional: specific division
    division = models.ForeignKey(
        HangarDivision,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Thresholds
    value_threshold = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True
    )
    quantity_threshold = models.BigIntegerField(null=True, blank=True)
    
    # Who to notify
    notify_users = models.ManyToManyField(User, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Alert Rule"
        verbose_name_plural = "Alert Rules"
        ordering = ["corporation", "name"]
    
    def __str__(self):
        return f"{self.corporation.corporation_name} - {self.name}"
