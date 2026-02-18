"""
Celery tasks for Corp Inventory
"""

import logging
from datetime import timedelta
from decimal import Decimal

from celery import shared_task
from django.utils import timezone
from django.db import transaction
from esi.models import Token

from .models import (
    Corporation,
    HangarDivision,
    Location,
    HangarItem,
    HangarTransaction,
    HangarSnapshot,
    AlertRule,
)
from .managers import CorpInventoryManager, PriceManager
from . import app_settings

logger = logging.getLogger(__name__)


@shared_task
def sync_all_corporations():
    """
    Sync all tracked corporations
    """
    corporations = Corporation.objects.filter(tracking_enabled=True)
    logger.info(f"Syncing {corporations.count()} corporations")
    
    for corp in corporations:
        sync_corporation_hangar.delay(corp.corporation_id)


@shared_task
def sync_corporation_hangar(corporation_id: int):
    """
    Sync a single corporation's hangar data
    
    Args:
        corporation_id: Corporation ID to sync
        
    Returns:
        Dict with sync status and message
    """
    try:
        corporation = Corporation.objects.get(corporation_id=corporation_id)
        
        if not corporation.tracking_enabled:
            msg = f"Skipping disabled corporation {corporation.corporation_name}"
            logger.info(msg)
            return {"status": "skipped", "message": msg}
        
        # Get a valid token for this corporation
        token = get_corporation_token(corporation_id)
        if not token:
            msg = f"No valid token found for corporation {corporation_id}"
            logger.error(msg)
            return {"status": "error", "message": msg}
        
        logger.info(f"Starting sync for {corporation.corporation_name}")
        
        # Fetch divisions first
        sync_divisions(corporation, token)
        
        # Fetch and process assets
        assets = CorpInventoryManager.get_corporation_assets(token, corporation_id)
        if not assets:
            msg = f"No assets returned for {corporation.corporation_name}"
            logger.warning(msg)
            corporation.last_sync = timezone.now()
            corporation.save()
            return {"status": "warning", "message": msg, "assets_count": 0}
        
        # Get market prices for valuation
        market_prices = PriceManager.get_market_prices()
        
        # Process assets and detect changes
        with transaction.atomic():
            items_count = process_assets(corporation, assets, market_prices, token)
        
        # Update last sync time
        corporation.last_sync = timezone.now()
        corporation.save()
        
        msg = f"Completed sync for {corporation.corporation_name} - {items_count} items processed"
        logger.info(msg)
        return {"status": "success", "message": msg, "assets_count": items_count}
        
    except Corporation.DoesNotExist:
        msg = f"Corporation {corporation_id} not found"
        logger.error(msg)
        return {"status": "error", "message": msg}
    except Exception as e:
        msg = f"Error syncing corporation {corporation_id}: {str(e)}"
        logger.error(msg, exc_info=True)
        return {"status": "error", "message": msg}


def get_corporation_token(corporation_id: int) -> Token:
    """
    Get a valid ESI token for a corporation
    
    Args:
        corporation_id: Corporation ID
        
    Returns:
        Valid Token object or None
    """
    # Look for a token with the required scopes for this corporation
    # We need a token from a character that belongs to the corporation
    required_scopes = app_settings.CORPINVENTORY_ESI_SCOPES
    
    try:
        # Try to find characters in this corporation
        from allianceauth.eveonline.models import EveCharacter
        
        characters = EveCharacter.objects.filter(
            corporation_id=corporation_id
        ).values_list('character_id', flat=True)
        
        if not characters:
            logger.warning(f"No characters found for corporation {corporation_id}")
            return None
        
        # Find valid tokens for these characters with required scopes
        tokens = Token.objects.filter(
            character_id__in=characters
        ).require_scopes(required_scopes).require_valid()
        
        if tokens.exists():
            return tokens.first()
        
        logger.warning(
            f"No valid tokens with required scopes found for corporation {corporation_id}"
        )
        return None
        
    except Exception as e:
        logger.error(f"Error getting token for corporation {corporation_id}: {e}")
        return None


def sync_divisions(corporation: Corporation, token: Token):
    """
    Sync hangar divisions for a corporation
    
    Args:
        corporation: Corporation object
        token: ESI token
    """
    try:
        divisions_data = CorpInventoryManager.get_corporation_divisions(
            token,
            corporation.corporation_id
        )
        
        if "hangar" in divisions_data:
            for div in divisions_data["hangar"]:
                HangarDivision.objects.update_or_create(
                    corporation=corporation,
                    division_id=div["division"],
                    defaults={"division_name": div.get("name", f"Division {div['division']}")}
                )
        
    except Exception as e:
        logger.error(f"Error syncing divisions for {corporation.corporation_name}: {e}")


def process_assets(
    corporation: Corporation,
    assets: list,
    market_prices: dict,
    token: Token
):
    """
    Process assets and detect changes
    
    Args:
        corporation: Corporation object
        assets: List of asset dictionaries from ESI
        market_prices: Dictionary of market prices
        token: ESI token
    """
    # Filter for hangar items only (location_flag starts with 'CorpSAG')
    hangar_assets = [
        asset for asset in assets
        if asset.get("location_flag", "").startswith("CorpSAG")
    ]
    
    logger.info(f"Processing {len(hangar_assets)} hangar assets")
    
    # Build snapshot data
    current_snapshot = {}
    locations_to_fetch = set()
    types_to_fetch = set()
    
    # First pass: collect IDs we need to fetch
    for asset in hangar_assets:
        locations_to_fetch.add(asset["location_id"])
        types_to_fetch.add(asset["type_id"])
    
    # Fetch and cache location data
    location_cache = {}
    for loc_id in locations_to_fetch:
        location = get_or_create_location(loc_id, token)
        if location:
            location_cache[loc_id] = location
    
    # Fetch and cache type data
    type_cache = {}
    for type_id in types_to_fetch:
        type_info = CorpInventoryManager.get_type_info(type_id)
        if type_info:
            type_cache[type_id] = type_info.get("name", f"Unknown Type {type_id}")
    
    # Mark all existing items as inactive
    HangarItem.objects.filter(
        corporation=corporation,
        is_active=True
    ).update(is_active=False)
    
    # Process each asset
    for asset in hangar_assets:
        item_id = asset["item_id"]
        type_id = asset["type_id"]
        quantity = asset.get("quantity", 1)
        location_id = asset["location_id"]
        
        # Get location
        location = location_cache.get(location_id)
        if not location:
            logger.warning(f"Skipping asset {item_id} - no location data")
            continue
        
        # Get type name
        type_name = type_cache.get(type_id, f"Unknown Type {type_id}")
        
        # Get division if available
        division = None
        location_flag = asset.get("location_flag", "")
        if location_flag.startswith("CorpSAG"):
            try:
                div_num = int(location_flag.replace("CorpSAG", ""))
                division = HangarDivision.objects.filter(
                    corporation=corporation,
                    division_id=div_num
                ).first()
            except (ValueError, HangarDivision.DoesNotExist):
                pass
        
        # Calculate estimated value
        unit_price = market_prices.get(type_id, 0)
        estimated_value = Decimal(str(unit_price)) * quantity
        
        # Check if item exists
        try:
            hangar_item = HangarItem.objects.get(item_id=item_id)
            old_quantity = hangar_item.quantity
            
            # Detect quantity change
            if old_quantity != quantity:
                create_transaction(
                    corporation=corporation,
                    transaction_type="CHANGE",
                    type_id=type_id,
                    type_name=type_name,
                    old_quantity=old_quantity,
                    new_quantity=quantity,
                    quantity_change=quantity - old_quantity,
                    location=location,
                    division=division,
                    estimated_value=estimated_value,
                )
            
            # Update item
            hangar_item.quantity = quantity
            hangar_item.estimated_value = estimated_value
            hangar_item.location = location
            hangar_item.division = division
            hangar_item.is_active = True
            hangar_item.save()
            
        except HangarItem.DoesNotExist:
            # New item detected
            hangar_item = HangarItem.objects.create(
                corporation=corporation,
                item_id=item_id,
                type_id=type_id,
                type_name=type_name,
                location=location,
                division=division,
                quantity=quantity,
                estimated_value=estimated_value,
                is_singleton=asset.get("is_singleton", False),
                is_blueprint_copy=asset.get("is_blueprint_copy", False),
                is_active=True,
            )
            
            # Create addition transaction
            create_transaction(
                corporation=corporation,
                transaction_type="ADD",
                type_id=type_id,
                type_name=type_name,
                old_quantity=0,
                new_quantity=quantity,
                quantity_change=quantity,
                location=location,
                division=division,
                estimated_value=estimated_value,
            )
        
        # Add to snapshot
        current_snapshot[item_id] = {
            "type_id": type_id,
            "type_name": type_name,
            "quantity": quantity,
            "value": float(estimated_value),
        }
    
    # Check for removed items (items that are now inactive)
    removed_items = HangarItem.objects.filter(
        corporation=corporation,
        is_active=False
    )
    
    for item in removed_items:
        create_transaction(
            corporation=corporation,
            transaction_type="REMOVE",
            type_id=item.type_id,
            type_name=item.type_name,
            old_quantity=item.quantity,
            new_quantity=0,
            quantity_change=-item.quantity,
            location=item.location,
            division=item.division,
            estimated_value=item.estimated_value,
        )
    
    # Create snapshot
    total_value = sum(item["value"] for item in current_snapshot.values())
    HangarSnapshot.objects.create(
        corporation=corporation,
        total_items=len(current_snapshot),
        total_value=Decimal(str(total_value)),
        snapshot_data=current_snapshot,
    )
    
    # Process alert rules
    process_alert_rules.delay(corporation.corporation_id)
    
    return len(current_snapshot)  # Return count of items processed


def get_or_create_location(location_id: int, token: Token) -> Location:
    """
    Get or create a Location object
    
    Args:
        location_id: Location ID
        token: ESI token
        
    Returns:
        Location object or None
    """
    try:
        return Location.objects.get(location_id=location_id)
    except Location.DoesNotExist:
        pass
    
    # Try to fetch location data
    location_data = None
    location_type = "unknown"
    
    # Check if it's a structure (> 1000000000000)
    if location_id >= 1000000000000:
        location_data = CorpInventoryManager.get_structure_info(token, location_id)
        location_type = "structure"
    else:
        location_data = CorpInventoryManager.get_station_info(location_id)
        location_type = "station"
    
    if not location_data:
        # Create placeholder
        return Location.objects.create(
            location_id=location_id,
            location_name=f"Unknown Location {location_id}",
            location_type=location_type,
        )
    
    # Get system info if available
    system_id = location_data.get("solar_system_id")
    system_name = ""
    region_id = None
    region_name = ""
    
    if system_id:
        system_info = CorpInventoryManager.get_solar_system_info(system_id)
        if system_info:
            system_name = system_info.get("name", "")
            constellation_id = system_info.get("constellation_id")
            
            # Get region from constellation
            if constellation_id:
                constellation_info = CorpInventoryManager.get_constellation_info(constellation_id)
                if constellation_info:
                    region_id = constellation_info.get("region_id")
                    if region_id:
                        region_info = CorpInventoryManager.get_region_info(region_id)
                        if region_info:
                            region_name = region_info.get("name", "")
    
    return Location.objects.create(
        location_id=location_id,
        location_name=location_data.get("name", f"Location {location_id}"),
        location_type=location_type,
        solar_system_id=system_id,
        solar_system_name=system_name,
        region_id=region_id,
        region_name=region_name,
    )


def create_transaction(**kwargs):
    """
    Create a hangar transaction record
    """
    transaction = HangarTransaction.objects.create(**kwargs)
    logger.debug(f"Created transaction: {transaction}")
    return transaction


@shared_task
def process_alert_rules(corporation_id: int):
    """
    Process alert rules for recent transactions
    
    Args:
        corporation_id: Corporation ID
    """
    try:
        corporation = Corporation.objects.get(corporation_id=corporation_id)
        
        # Get recent transactions (last 5 minutes)
        recent_time = timezone.now() - timedelta(minutes=5)
        recent_transactions = HangarTransaction.objects.filter(
            corporation=corporation,
            detected_at__gte=recent_time,
            notification_sent=False
        )
        
        if not recent_transactions.exists():
            return
        
        # Get active alert rules
        alert_rules = AlertRule.objects.filter(
            corporation=corporation,
            is_active=True
        )
        
        for rule in alert_rules:
            for trans in recent_transactions:
                if should_trigger_alert(rule, trans):
                    send_alert(rule, trans)
                    trans.notification_sent = True
                    trans.save()
        
    except Corporation.DoesNotExist:
        logger.error(f"Corporation {corporation_id} not found")
    except Exception as e:
        logger.error(f"Error processing alert rules: {e}", exc_info=True)


def should_trigger_alert(rule: AlertRule, transaction: HangarTransaction) -> bool:
    """
    Check if a transaction should trigger an alert rule
    
    Args:
        rule: AlertRule object
        transaction: HangarTransaction object
        
    Returns:
        True if alert should be triggered
    """
    # Check alert type
    if rule.alert_type == "ITEM_ADDED" and transaction.transaction_type != "ADD":
        return False
    
    if rule.alert_type == "ITEM_REMOVED" and transaction.transaction_type != "REMOVE":
        return False
    
    # Check type_id if specified
    if rule.type_id and rule.type_id != transaction.type_id:
        return False
    
    # Check division if specified
    if rule.division and rule.division != transaction.division:
        return False
    
    # Check value threshold
    if rule.value_threshold and transaction.estimated_value < rule.value_threshold:
        return False
    
    # Check quantity threshold
    if rule.quantity_threshold:
        if abs(transaction.quantity_change) < rule.quantity_threshold:
            return False
    
    return True


def send_alert(rule: AlertRule, transaction: HangarTransaction):
    """
    Send alert notification
    
    Args:
        rule: AlertRule object
        transaction: HangarTransaction object
    """
    # TODO: Implement notification system
    # This would typically use Alliance Auth's notification system
    logger.info(f"Alert triggered: {rule.name} for transaction {transaction.id}")
    
    # Example notification (requires Alliance Auth notifications app)
    # from allianceauth.notifications import notify
    # for user in rule.notify_users.all():
    #     notify(
    #         user,
    #         f"Corp Inventory Alert: {rule.name}",
    #         message=f"{transaction}",
    #         level="warning"
    #     )
