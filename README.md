# Alliance Auth Corp Inventory

Track and monitor corporation hangar assets in EVE Online through Alliance Auth.

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Django](https://img.shields.io/badge/django-4.0+-blue)
![Alliance Auth](https://img.shields.io/badge/allianceauth-3.0+-blue)

## Features

- **Hangar Inventory Tracking**: View all items across corporation hangars at any station
- **Transaction Logging**: Track who adds and removes items from hangars
- **Multi-Location Support**: Monitor assets across multiple stations and structures
- **Division Filtering**: Filter items by hangar division
- **Value Estimation**: Automatic ISK valuation of hangar contents
- **Search & Filter**: Powerful search and filter capabilities
- **Alert Rules**: Configure custom alerts for specific items or conditions
- **Transaction History**: Detailed logs of all hangar changes
- **Statistics Dashboard**: Analytics and insights on hangar activity
- **ESI Integration**: Uses EVE Online's ESI API for real-time data

## Screenshots

![Dashboard](docs/screenshots/dashboard.png)
![Hangar View](docs/screenshots/hangar.png)
![Transactions](docs/screenshots/transactions.png)

## Installation

### Requirements

- Alliance Auth >= 3.0.0
- Python >= 3.8
- Django >= 4.0

### Step 1: Install from GitHub
Install:
```bash
docker compose exec allianceauth_gunicorn bash
```

```bash
pip install git+https://github.com/Thrainkrilleve/corp-inventory.git
```

### Step 2: Configure Alliance Auth

Add `corp_inventory` to your `INSTALLED_APPS` in your Alliance Auth `local.py` settings file:

```python
INSTALLED_APPS = [
    # ... other apps
    'corp_inventory',
]
```
```
Add git+https://github.com/Thrainkrilleve/corp-inventory.git to requirements.txt

```
### Step 3: Configure ESI Scopes

The app requires the following ESI scopes:
- `esi-assets.read_corporation_assets.v1`
- `esi-corporations.read_divisions.v1`
- `esi-universe.read_structures.v1`

### Step 4: Run Migrations

```bash
python manage.py migrate corp_inventory
```

### Step 5: Collect Static Files

```bash
python manage.py collectstatic
```

### Step 6: Restart Services

Restart your Alliance Auth services

### Step 7: Configure Permissions

Grant permissions to users/groups in Alliance Auth admin:

- `corp_inventory.basic_access` - Basic access to the app
- `corp_inventory.view_hangar` - View corporation hangars
- `corp_inventory.view_transactions` - View transaction logs
- `corp_inventory.manage_tracking` - Manage hangar tracking settings
- `corp_inventory.manage_corporations` - Add/remove tracked corporations

### Step 8: Set Up Corporations

**Option A: Through the App (Recommended)**
1. Navigate to Corp Inventory in Alliance Auth
2. Click "Manage Corporations"
3. Enter your corporation ID, name, and ticker
4. Add an ESI token from a corporation Director/CEO character
5. Click "Sync Now"

**Option B: Through Django Admin**
1. Log in to Django admin
2. Navigate to Corp Inventory → Corporations
3. Add your corporation(s) to track
4. Ensure a Director/CEO character has added an ESI token
5. Enable tracking for each corporation

### Step 9: Add ESI Token

**Critical:** You must add an ESI token from a corporation Director or CEO:

1. Have a Director/CEO character authenticate with Alliance Auth
2. Go to Alliance Auth ESI Tokens page
3. Add a token with required scopes
4. The app will automatically find and use this token

## Updating

### Standard Update Process

To update to the latest version:

```bash
# Update the package
pip install --upgrade git+https://github.com/Thrainkrilleve/corp-inventory.git

# Run any new migrations
python manage.py migrate

# Collect new static files
python manage.py collectstatic --noinput

# Restart services
supervisorctl restart myauth:
```

### Docker Update Process

If using Docker/Docker Compose:

```bash


#Enter venv
docker compose exec allianceauth_gunicorn bash

# Run migrations
auth migrate

# Collect static files
auth collectstatic --noinput

#exit venv
exit

# Rebuild containers (picks up new requirements.txt)
docker compose build

# Restart services
docker compose restart
```

### After Updating

1. Check the [CHANGELOG.md](CHANGELOG.md) for any breaking changes
2. Verify static files are updated: `python manage.py collectstatic`
3. Visit the **Diagnostics & Logs** page in the app to verify everything is working
4. Check for any new permissions that need to be granted

### Checking Current Version

In the Django shell:

```python
python manage.py shell

import corp_inventory
print(corp_inventory.__version__)
```

## Configuration

Optional settings in your `local.py`:

```python
# How often to sync hangar data (in minutes)
CORPINVENTORY_SYNC_INTERVAL = 30

# Maximum age of data before requiring refresh (in hours)
CORPINVENTORY_DATA_MAX_AGE = 24

# Enable notifications for hangar transactions
CORPINVENTORY_ENABLE_NOTIFICATIONS = True

# Minimum value (ISK) for transaction alerts
CORPINVENTORY_ALERT_THRESHOLD = 100000000  # 100M ISK
```

## Usage

### Automatic Syncing

The app will automatically sync corporation hangar data based on the configured interval. You can also manually trigger a sync from the web interface if you have the appropriate permissions.

### Setting Up Alert Rules

1. Go to Django admin > Corp Inventory > Alert Rules
2. Create a new alert rule
3. Configure the conditions (item type, value threshold, etc.)
4. Select users to notify
5. Save and activate the rule

### Viewing Hangars

1. Navigate to Corp Inventory from the main menu
2. Select a corporation to view
3. Use filters to narrow down items by division, location, or search
4. Click on any item for detailed history

### Transaction Logs

Transaction logs automatically capture:
- Item additions to hangars
- Item removals from hangars
- Quantity changes
- Estimated value of transactions

## Periodic Tasks

The app uses Celery to run periodic sync tasks. Make sure your Alliance Auth Celery beat scheduler is running.

Add to your `local.py` settings:

```python
CELERYBEAT_SCHEDULE['corp_inventory_sync'] = {
    'task': 'corp_inventory.tasks.sync_all_corporations',
    'schedule': crontab(minute='*/30'),  # Run every 30 minutes
}
```

## Troubleshooting

### Use the Built-in Diagnostics Page

Navigate to **Corp Inventory → Diagnostics & Logs** to check:
- Valid ESI tokens for each corporation
- Character authentication status
- Corporation configuration
- Last sync times
- Item and transaction counts
- Recent log entries
- Common issues with solutions

**This should be your first stop when debugging sync issues!**

### Viewing Logs

**In the App:**
- Go to Corp Inventory → Diagnostics & Logs
- Scroll to "Recent Log Entries" section
- Shows last 100 log lines from the app

**Via Command Line:**

```bash
# Docker
docker logs -f allianceauth_beat
docker logs -f allianceauth_worker

# Systemd
journalctl -u allianceauth-beat -f
journalctl -u allianceauth-worker -f

# Django logs (if file logging enabled)
tail -f /path/to/your/logs/django.log
```

**Manual Test Sync:**

```bash
python manage.py shell

from corp_inventory.tasks import sync_all_corporations
sync_all_corporations()
# Watch output for errors
```

### Common Issues

1. **No valid token found**
   - A Corporation Director or CEO must authenticate with Alliance Auth
   - They must add an ESI token with all required scopes:
     - `esi-assets.read_corporation_assets.v1`
     - `esi-corporations.read_divisions.v1`
     - `esi-universe.read_structures.v1`
   - Token must not be expired
   - **Fix:** Have Director/CEO add token via Alliance Auth dashboard

2. **No characters found**
   - No one from the corporation has authenticated with Alliance Auth
   - **Fix:** Have a Director/CEO log in and add their character

3. **Sync completes but no items appear**
   - Check that items are in corporation hangars (not personal hangars)
   - Items must be in CorpSAG1-7 divisions
   - Items in containers may not appear
   - Check the diagnostics page for item counts
   - **Fix:** View diagnostics page, check logs for ESI errors

4. **"Items in Database: 0" after sync**
   - Token may not have correct permissions
   - Character may not be a Director/CEO
   - Corporation may genuinely have empty hangars
   - **Fix:** Check diagnostics page, verify token scopes

5. **Static files not loading (CSS/JS broken)**
   - Run `python manage.py collectstatic`
   - Restart your web server
   - Check static files configuration in `local.py`
   - The diagnostics page will show if tokens are valid

### No Items Appearing

1. **Verify items are in corporation hangars**
   - Items must be in CorpSAG1-7 (corporation hangars)
   - Items in containers or personal hangars won't appear

2. **Check sync status**
   - Use the Diagnostics page to verify sync completed successfully
   - Look for error messages in the diagnostics

3. **Database migration issue**
   - Early versions had a migration bug with `division_id`
   - If you installed before the fix, run: `python manage.py migrate corp_inventory --fake-initial`
   - Then run: `python manage.py migrate corp_inventory`

### Token/Permission Issues

**Token expired or invalid:**
- Have the character owner log out and back into Alliance Auth
- Re-add their ESI token with all required scopes
- Check the Diagnostics page to verify token is valid

**Missing ESI scopes:**
Required scopes:
- `esi-assets.read_corporation_assets.v1`
- `esi-corporations.read_divisions.v1`
- `esi-universe.read_structures.v1`

### Performance

For large inventories (10,000+ items):
- Increase `CORPINVENTORY_SYNC_INTERVAL` to reduce frequency
- Consider adding database indexes (already included in migrations)
- Monitor Celery worker performance

### Getting Help

1. Check the **Diagnostics** page in the app
2. Review Django logs for detailed error messages  
3. Check Celery logs: `tail -f /path/to/logs/celery.log`
4. Open an issue on GitHub with diagnostic information

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/allianceauth-corp-inventory.git
cd allianceauth-corp-inventory

# Install in editable mode
pip install -e .

# Install development dependencies
pip install -e .[dev]

# Set up pre-commit hooks
pre-commit install
```

### Running Tests

```bash
python runtests.py
```

### Code Style

This project uses:
- Black for code formatting
- isort for import sorting
- flake8 for linting

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

- Built for [Alliance Auth](https://gitlab.com/allianceauth/allianceauth)
- EVE Online and the EVE logo are the registered trademarks of CCP hf.

## Changelog

### Version 0.1.0

- Initial release
- Corporation hangar tracking
- Transaction logging
- Alert rules
- Search and filtering
- Statistics dashboard

## Support

For issues, questions, or feature requests, please use the [GitHub issue tracker](https://github.com/yourusername/allianceauth-corp-inventory/issues).
