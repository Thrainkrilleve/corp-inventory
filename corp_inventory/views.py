"""
Views for Corp Inventory
"""

import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from datetime import timedelta

from . import app_settings
from .models import (
    Corporation,
    HangarDivision,
    Location,
    HangarItem,
    HangarTransaction,
    HangarSnapshot,
    AlertRule,
)
from .tasks import sync_corporation_hangar

logger = logging.getLogger(__name__)


@login_required
@permission_required("corp_inventory.basic_access", raise_exception=True)
def index(request):
    """
    Main dashboard view showing overview of tracked corporations
    """
    # Get corporations the user has access to
    # For now, showing all tracked corporations
    # You may want to filter based on user's corporation membership
    corporations = Corporation.objects.filter(tracking_enabled=True)
    
    # Get statistics for each corporation
    corp_stats = []
    for corp in corporations:
        active_items = HangarItem.objects.filter(
            corporation=corp,
            is_active=True
        ).count()
        
        total_value = HangarItem.objects.filter(
            corporation=corp,
            is_active=True
        ).aggregate(total=Sum('estimated_value'))['total'] or 0
        
        recent_transactions = HangarTransaction.objects.filter(
            corporation=corp,
            detected_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        corp_stats.append({
            'corporation': corp,
            'active_items': active_items,
            'total_value': total_value,
            'recent_transactions': recent_transactions,
            'last_sync': corp.last_sync,
        })
    
    context = {
        'corp_stats': corp_stats,
        'title': 'Corp Inventory Dashboard',
        'one_hour_ago': timezone.now() - timedelta(hours=1),
    }
    
    return render(request, 'corp_inventory/index.html', context)


@login_required
@permission_required("corp_inventory.view_hangar", raise_exception=True)
def corporation_hangar(request, corporation_id):
    """
    View hangar contents for a specific corporation
    """
    corporation = get_object_or_404(Corporation, corporation_id=corporation_id)
    
    # Get filter parameters
    division_filter = request.GET.get('division')
    location_filter = request.GET.get('location')
    search_query = request.GET.get('search')
    
    # Base queryset
    items = HangarItem.objects.filter(
        corporation=corporation,
        is_active=True
    ).select_related('location', 'division')
    
    # Apply filters
    if division_filter:
        items = items.filter(division_id=division_filter)
    
    if location_filter:
        items = items.filter(location_id=location_filter)
    
    if search_query:
        items = items.filter(
            Q(type_name__icontains=search_query) |
            Q(location__location_name__icontains=search_query)
        )
    
    # Get available divisions and locations for filters
    divisions = HangarDivision.objects.filter(corporation=corporation)
    locations = Location.objects.filter(
        items__corporation=corporation,
        items__is_active=True
    ).distinct()
    
    # Calculate totals
    total_value = items.aggregate(total=Sum('estimated_value'))['total'] or 0
    total_items = items.count()
    
    context = {
        'corporation': corporation,
        'items': items,
        'divisions': divisions,
        'locations': locations,
        'total_value': total_value,
        'total_items': total_items,
        'title': f'{corporation.corporation_name} Hangar',
        'selected_division': division_filter,
        'selected_location': location_filter,
        'search_query': search_query,
    }
    
    return render(request, 'corp_inventory/hangar.html', context)


@login_required
@permission_required("corp_inventory.view_transactions", raise_exception=True)
def transaction_log(request, corporation_id=None):
    """
    View transaction history
    """
    # Base queryset
    transactions = HangarTransaction.objects.all().select_related(
        'corporation', 'location', 'division'
    )
    
    # Filter by corporation if specified
    corporation = None
    if corporation_id:
        corporation = get_object_or_404(Corporation, corporation_id=corporation_id)
        transactions = transactions.filter(corporation=corporation)
    
    # Get filter parameters
    transaction_type = request.GET.get('type')
    days_back = request.GET.get('days', '7')
    item_search = request.GET.get('search')
    character_search = request.GET.get('character')
    
    # Apply filters
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    try:
        days = int(days_back)
        cutoff_date = timezone.now() - timedelta(days=days)
        transactions = transactions.filter(detected_at__gte=cutoff_date)
    except ValueError:
        pass
    
    if item_search:
        transactions = transactions.filter(type_name__icontains=item_search)
    
    if character_search:
        transactions = transactions.filter(character_name__icontains=character_search)
    
    # Order by most recent first
    transactions = transactions.order_by('-detected_at')[:500]  # Limit to 500
    
    # Get available corporations for filter
    corporations = Corporation.objects.filter(tracking_enabled=True)
    
    context = {
        'transactions': transactions,
        'corporation': corporation,
        'corporations': corporations,
        'title': 'Transaction Log',
        'selected_type': transaction_type,
        'days_back': days_back,
        'search_query': item_search,
        'character_search': character_search,
    }
    
    return render(request, 'corp_inventory/transactions.html', context)


@login_required
@permission_required("corp_inventory.view_hangar", raise_exception=True)
def item_details(request, item_id):
    """
    View details and history for a specific item
    """
    item = get_object_or_404(HangarItem, item_id=item_id)
    
    # Get transaction history for this item type at this location
    transactions = HangarTransaction.objects.filter(
        corporation=item.corporation,
        type_id=item.type_id,
        location=item.location
    ).order_by('-detected_at')[:50]
    
    context = {
        'item': item,
        'transactions': transactions,
        'title': f'Item Details: {item.type_name}',
    }
    
    return render(request, 'corp_inventory/item_details.html', context)


@login_required
@permission_required("corp_inventory.manage_tracking", raise_exception=True)
def sync_corporation(request, corporation_id):
    """
    Manually trigger a sync for a corporation
    """
    corporation = get_object_or_404(Corporation, corporation_id=corporation_id)
    
    # Trigger sync task
    sync_corporation_hangar.delay(corporation_id)
    
    messages.success(
        request,
        f"Sync initiated for {corporation.corporation_name}. "
        f"This may take a few minutes."
    )
    
    # Redirect back to the corporation hangar view
    return redirect('corp_inventory:corporation_hangar', corporation_id=corporation_id)


@login_required
@permission_required("corp_inventory.view_hangar", raise_exception=True)
def location_view(request, location_id):
    """
    View all items at a specific location across all corporations
    """
    location = get_object_or_404(Location, location_id=location_id)
    
    items = HangarItem.objects.filter(
        location=location,
        is_active=True
    ).select_related('corporation', 'division')
    
    # Group by corporation
    corp_items = {}
    for item in items:
        corp_name = item.corporation.corporation_name
        if corp_name not in corp_items:
            corp_items[corp_name] = []
        corp_items[corp_name].append(item)
    
    total_value = items.aggregate(total=Sum('estimated_value'))['total'] or 0
    
    context = {
        'location': location,
        'corp_items': corp_items,
        'total_items': items.count(),
        'total_value': total_value,
        'title': f'Location: {location.location_name}',
    }
    
    return render(request, 'corp_inventory/location.html', context)


@login_required
@permission_required("corp_inventory.view_hangar", raise_exception=True)
def statistics(request, corporation_id):
    """
    View statistics and charts for a corporation
    """
    corporation = get_object_or_404(Corporation, corporation_id=corporation_id)
    
    # Get recent snapshots
    snapshots = HangarSnapshot.objects.filter(
        corporation=corporation
    ).order_by('-snapshot_time')[:30]
    
    # Top items by value
    top_items = HangarItem.objects.filter(
        corporation=corporation,
        is_active=True
    ).order_by('-estimated_value')[:10]
    
    # Transaction summary
    transaction_summary = {}
    for trans_type, label in HangarTransaction.TRANSACTION_TYPE_CHOICES:
        count = HangarTransaction.objects.filter(
            corporation=corporation,
            transaction_type=trans_type,
            detected_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        transaction_summary[label] = count
    
    # Active alert rules
    alert_rules = AlertRule.objects.filter(
        corporation=corporation,
        is_active=True
    )
    
    context = {
        'corporation': corporation,
        'snapshots': snapshots,
        'top_items': top_items,
        'transaction_summary': transaction_summary,
        'alert_rules': alert_rules,
        'title': f'{corporation.corporation_name} Statistics',
    }
    
    return render(request, 'corp_inventory/statistics.html', context)


@login_required
@permission_required("corp_inventory.view_hangar", raise_exception=True)
def api_hangar_data(request, corporation_id):
    """
    API endpoint to get hangar data as JSON for AJAX requests
    """
    corporation = get_object_or_404(Corporation, corporation_id=corporation_id)
    
    items = HangarItem.objects.filter(
        corporation=corporation,
        is_active=True
    ).select_related('location', 'division')
    
    data = []
    for item in items:
        data.append({
            'item_id': item.item_id,
            'type_id': item.type_id,
            'type_name': item.type_name,
            'quantity': item.quantity,
            'location': item.location.location_name,
            'division': item.division.division_name if item.division else '',
            'value': float(item.estimated_value),
        })
    
    return JsonResponse({'items': data})


@login_required
@permission_required("corp_inventory.manage_corporations", raise_exception=True)
def manage_corporations(request):
    """
    View to manage tracked corporations
    """
    if request.method == 'POST':
        # Add new corporation
        corp_id = request.POST.get('corporation_id')
        corp_name = request.POST.get('corporation_name')
        ticker = request.POST.get('ticker', '')
        
        if corp_id and corp_name:
            try:
                corporation, created = Corporation.objects.get_or_create(
                    corporation_id=corp_id,
                    defaults={
                        'corporation_name': corp_name,
                        'ticker': ticker,
                        'tracking_enabled': True,
                    }
                )
                
                if created:
                    messages.success(
                        request,
                        f'Successfully added {corp_name} for tracking!'
                    )
                    # Trigger initial sync
                    sync_corporation_hangar.delay(int(corp_id))
                else:
                    messages.info(
                        request,
                        f'{corp_name} is already being tracked.'
                    )
            except Exception as e:
                logger.error(f"Error adding corporation: {e}")
                messages.error(
                    request,
                    f'Error adding corporation: {str(e)}'
                )
        else:
            messages.error(request, 'Corporation ID and Name are required.')
        
        return redirect('corp_inventory:manage_corporations')
    
    # GET request - show all corporations
    corporations = Corporation.objects.all().order_by('-tracking_enabled', 'corporation_name')
    
    esi_token_url = getattr(
        app_settings,
        "CORPINVENTORY_ESI_TOKEN_URL",
        "/auth/eveauth/",
    )
    for url_name in (
        "esi:token_add",
        "esi:character_add",
        "eveonline:token_add",
        "eveonline:character_add",
    ):
        try:
            esi_token_url = reverse(url_name)
            break
        except NoReverseMatch:
            continue

    context = {
        'corporations': corporations,
        'title': 'Manage Corporations',
        'esi_token_url': esi_token_url,
    }
    
    return render(request, 'corp_inventory/manage_corporations.html', context)


@login_required
@permission_required("corp_inventory.manage_corporations", raise_exception=True)
def toggle_corporation_tracking(request, corporation_id):
    """
    Enable or disable tracking for a corporation
    """
    if request.method == 'POST':
        corporation = get_object_or_404(Corporation, corporation_id=corporation_id)
        corporation.tracking_enabled = not corporation.tracking_enabled
        corporation.save()
        
        status = 'enabled' if corporation.tracking_enabled else 'disabled'
        messages.success(
            request,
            f'Tracking {status} for {corporation.corporation_name}'
        )
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required
@permission_required("corp_inventory.manage_corporations", raise_exception=True)
def delete_corporation(request, corporation_id):
    """
    Delete a corporation and all associated data
    """
    corporation = get_object_or_404(Corporation, corporation_id=corporation_id)
    corp_name = corporation.corporation_name
    
    # Delete the corporation (cascade will handle related objects)
    corporation.delete()
    
    messages.success(
        request,
        f'Successfully removed {corp_name} and all associated data.'
    )
    
    return redirect('corp_inventory:manage_corporations')


@login_required
@permission_required("corp_inventory.manage_corporations", raise_exception=True)
def view_logs(request):
    """
    View sync logs and diagnostic information
    """
    from esi.models import Token
    from allianceauth.eveonline.models import EveCharacter
    import logging.handlers
    import os
    
    corporations = Corporation.objects.all()
    
    # Build diagnostic information
    diagnostics = []
    for corp in corporations:
        # Check for valid characters
        characters = EveCharacter.objects.filter(
            corporation_id=corp.corporation_id
        )
        
        # Check for valid tokens
        required_scopes = app_settings.CORPINVENTORY_ESI_SCOPES
        tokens = Token.objects.filter(
            character_id__in=characters.values_list('character_id', flat=True)
        ).require_scopes(required_scopes).require_valid()
        
        # Get item and transaction counts
        item_count = HangarItem.objects.filter(
            corporation=corp,
            is_active=True
        ).count()
        
        transaction_count = HangarTransaction.objects.filter(
            corporation=corp
        ).count()
        
        diagnostics.append({
            'corporation': corp,
            'character_count': characters.count(),
            'token_count': tokens.count(),
            'has_valid_token': tokens.exists(),
            'last_sync': corp.last_sync,
            'tracking_enabled': corp.tracking_enabled,
            'item_count': item_count,
            'transaction_count': transaction_count,
        })
    
    # Get recent log entries from the logger
    log_entries = []
    try:
        # Try to get logs from the Django logging handler
        for handler in logging.getLogger('corp_inventory').handlers:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                log_file = handler.baseFilename
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        log_entries = lines[-100:]  # Last 100 lines
                        log_entries.reverse()
    except Exception as e:
        logger.warning(f"Could not read log file: {e}")
    
    # Get filter parameters
    corporation_id = request.GET.get('corporation_id', '')
    
    context = {
        'corporations': corporations,
        'diagnostics': diagnostics,
        'corporation_id': corporation_id,
        'required_scopes': app_settings.CORPINVENTORY_ESI_SCOPES,
        'log_entries': log_entries,
        'title': 'Sync Logs & Diagnostics',
    }
    
    return render(request, 'corp_inventory/logs.html', context)
