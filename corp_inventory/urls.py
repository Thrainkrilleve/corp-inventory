"""
URL Configuration for Corp Inventory
"""

from django.urls import path

from . import views

app_name = 'corp_inventory'

urlpatterns = [
    # Main dashboard
    path('', views.index, name='index'),
    
    # Corporation hangar views
    path(
        'corporation/<int:corporation_id>/',
        views.corporation_hangar,
        name='corporation_hangar'
    ),
    path(
        'corporation/<int:corporation_id>/sync/',
        views.sync_corporation,
        name='sync_corporation'
    ),
    path(
        'corporation/<int:corporation_id>/statistics/',
        views.statistics,
        name='statistics'
    ),
    
    # Transaction log
    path('transactions/', views.transaction_log, name='transactions'),
    path(
        'transactions/<int:corporation_id>/',
        views.transaction_log,
        name='corporation_transactions'
    ),
    
    # Item details
    path('item/<int:item_id>/', views.item_details, name='item_details'),
    
    # Location view
    path('location/<int:location_id>/', views.location_view, name='location'),
    
    # API endpoints
    path(
        'api/hangar/<int:corporation_id>/',
        views.api_hangar_data,
        name='api_hangar_data'
    ),
    
    # Corporation management
    path('manage/', views.manage_corporations, name='manage_corporations'),
    path(
        'manage/toggle/<int:corporation_id>/',
        views.toggle_corporation_tracking,
        name='toggle_corporation_tracking'
    ),
    path(
        'manage/delete/<int:corporation_id>/',
        views.delete_corporation,
        name='delete_corporation'
    ),
    
    # ESI token add (triggers EVE SSO flow)
    path('manage/add-token/', views.add_corp_token, name='add_corp_token'),

    # Container access logs
    path(
        'corporation/<int:corporation_id>/container-logs/',
        views.container_logs,
        name='container_logs'
    ),

    # Diagnostics
    path('logs/', views.view_logs, name='logs'),
]
