# Installation Guide

Detailed installation guide for Alliance Auth Corp Inventory.

## Prerequisites

- Alliance Auth 3.0 or higher installed and configured
- Python 3.8 or higher
- Access to corporation with required ESI scopes
- Corporation director role (for ESI token authentication)

## Step-by-Step Installation

### 1. Install the Package

Using pip in your Alliance Auth virtual environment:

```bash
pip install allianceauth-corp-inventory
```

Or install from source:

```bash
git clone https://github.com/yourusername/allianceauth-corp-inventory.git
cd allianceauth-corp-inventory
pip install -e .
```

### 2. Add to INSTALLED_APPS

Edit your Alliance Auth `myauth/settings/local.py` file:

```python
INSTALLED_APPS = [
    # ... existing apps
    'corp_inventory',  # Add this line
]
```

### 3. Configure ESI Scopes

The app requires these ESI scopes:
- `esi-assets.read_corporation_assets.v1`
- `esi-corporations.read_divisions.v1`

Add these to your ESI application at https://developers.eveonline.com

### 4. Run Migrations

```bash
python manage.py migrate corp_inventory
```

Expected output:
```
Running migrations:
  Applying corp_inventory.0001_initial... OK
```

### 5. Collect Static Files

```bash
python manage.py collectstatic
```

### 6. Restart Services

```bash
supervisorctl restart myauth:
supervisorctl restart myauth-worker:
supervisorctl restart myauth-beat:
```

### 7. Configure Permissions

In Alliance Auth admin panel:

1. Go to **Authentication & Authorization** > **Groups**
2. Select the group you want to grant access
3. Add permissions:
   - `corp_inventory | basic_access` - Basic app access
   - `corp_inventory | view_hangar` - View hangars
   - `corp_inventory | view_transactions` - View transactions
   - `corp_inventory | manage_tracking` - Manage tracking settings

### 8. Add Corporations to Track

1. Go to Django Admin > **Corp Inventory** > **Corporations**
2. Click **Add Corporation**
3. Enter:
   - Corporation ID
   - Corporation Name
   - Enable tracking
4. Save

### 9. Configure ESI Tokens

Corporation directors need to:

1. Log in to Alliance Auth
2. Go to **Services** > **EVE SSO**
3. Add a character with director roles
4. Ensure the character is in the tracked corporation

The app will automatically use valid tokens for syncing.

### 10. Initial Sync

Trigger the first sync manually:

1. Navigate to Corp Inventory from the sidebar
2. Select a corporation
3. Click **Sync Now**

Or run via Django shell:

```bash
python manage.py shell
```

```python
from corp_inventory.tasks import sync_corporation_hangar
sync_corporation_hangar.delay(YOUR_CORP_ID)
```

## Configuration Options

Add to `local.py` to customize:

```python
# Sync interval in minutes (default: 30)
CORPINVENTORY_SYNC_INTERVAL = 30

# Data max age in hours (default: 24)
CORPINVENTORY_DATA_MAX_AGE = 24

# Enable notifications (default: True)
CORPINVENTORY_ENABLE_NOTIFICATIONS = True

# Alert threshold in ISK (default: 100M)
CORPINVENTORY_ALERT_THRESHOLD = 100000000
```

## Celery Configuration

The app uses Celery beat for scheduled tasks. Ensure in your `local.py`:

```python
from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    # ... existing tasks
    'corp_inventory_sync_all': {
        'task': 'corp_inventory.tasks.sync_all_corporations',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
}
```

## Troubleshooting

### "No module named 'corp_inventory'"

- Ensure the package is installed in the correct virtual environment
- Verify `corp_inventory` is in INSTALLED_APPS
- Restart services

### "No valid token found"

- Ensure a corporation director has authenticated
- Check ESI scopes are correctly configured
- Verify the character is in the tracked corporation

### "Permission denied"

- Grant appropriate permissions to user groups
- Check user has `basic_access` permission at minimum

### Sync not running automatically

- Check Celery beat is running: `supervisorctl status myauth-beat`
- Verify CELERYBEAT_SCHEDULE is configured
- Check Celery logs for errors

## Verification

To verify installation:

1. Check the sidebar for **Corp Inventory** menu item
2. Click it - you should see the dashboard
3. Admin panel should have **Corp Inventory** section
4. Celery logs should show sync tasks running

## Upgrade

To upgrade to a newer version:

```bash
pip install --upgrade allianceauth-corp-inventory
python manage.py migrate corp_inventory
python manage.py collectstatic --noinput
supervisorctl restart myauth:
```

## Uninstallation

To remove the app:

1. Remove `corp_inventory` from INSTALLED_APPS
2. Run migrations backwards (optional):
   ```bash
   python manage.py migrate corp_inventory zero
   ```
3. Uninstall package:
   ```bash
   pip uninstall allianceauth-corp-inventory
   ```
4. Restart services

## Support

For help:
- Check the [README](README.md)
- Review [GitHub Issues](https://github.com/yourusername/allianceauth-corp-inventory/issues)
- Ask in Alliance Auth Discord
