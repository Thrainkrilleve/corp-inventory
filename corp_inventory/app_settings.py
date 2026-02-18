"""
App settings for Corp Inventory
"""

from django.conf import settings

# ESI Scopes required for this app
CORPINVENTORY_ESI_SCOPES = [
    "esi-assets.read_corporation_assets.v1",
    "esi-corporations.read_divisions.v1",
]

# How often to sync hangar data (in minutes)
CORPINVENTORY_SYNC_INTERVAL = getattr(
    settings,
    "CORPINVENTORY_SYNC_INTERVAL",
    30,
)

# Maximum age of data before requiring a refresh (in hours)
CORPINVENTORY_DATA_MAX_AGE = getattr(
    settings,
    "CORPINVENTORY_DATA_MAX_AGE",
    24,
)

# Enable notifications for hangar transactions
CORPINVENTORY_ENABLE_NOTIFICATIONS = getattr(
    settings,
    "CORPINVENTORY_ENABLE_NOTIFICATIONS",
    True,
)

# Minimum value (ISK) for transaction alerts
CORPINVENTORY_ALERT_THRESHOLD = getattr(
    settings,
    "CORPINVENTORY_ALERT_THRESHOLD",
    100000000,  # 100M ISK
)
