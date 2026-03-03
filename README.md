# Alliance Auth Corp Inventory

Track and monitor corporation hangar assets in EVE Online through Alliance Auth.

![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-0.1.31-blue)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Django](https://img.shields.io/badge/django-4.2+-blue)
![Alliance Auth](https://img.shields.io/badge/allianceauth-4.0+-blue)

## Features

- **Hangar Inventory Tracking**  View all items across corporation hangars at any station or structure
- **Transaction Logging**  Automatically records additions, removals, quantity changes, and item movements between locations
- **Container Access Logs**  View ESI container access logs showing who interacted with secured containers
- **Multi-Location Support**  Monitor assets across multiple stations and player-owned structures
- **Division Filtering**  Filter items by hangar division (SAG 17)
- **Value Estimation**  Automatic ISK valuation pulled from ESI market prices
- **Search & Filter**  Powerful search and filter capabilities across all views
- **Alert Rules**  Configure custom alerts for specific items or value thresholds
- **Statistics Dashboard**  Analytics and insights on hangar activity over time
- **ESI Integration**  Uses EVE Online's ESI API with Celery for automated background syncing
- **Optional SDE Integration**  Use [django-eveonline-sde](https://pypi.org/project/django-eveonline-sde/) for faster, ESI-free type name and location lookups

## Installation

### Requirements

- Alliance Auth >= 4.0.0
- Python >= 3.10
- Django >= 4.2

### Step 1: Install the Package

**Docker:**
```bash
docker compose exec allianceauth_gunicorn bash
pip install git+https://github.com/Thrainkrilleve/corp-inventory.git@v0.1.31
```

**Systemd / bare metal:**
```bash
pip install git+https://github.com/Thrainkrilleve/corp-inventory.git@v0.1.31
```

To pin this in a `requirements.txt`:
```
allianceauth-corp-inventory @ git+https://github.com/Thrainkrilleve/corp-inventory.git@v0.1.31
```

### Step 2: Configure Alliance Auth

Add `corp_inventory` to your `INSTALLED_APPS` in `myauth/settings/local.py`:

```python
INSTALLED_APPS = [
    # ... other apps
    'corp_inventory',
]
```

### Step 3: Configure ESI Scopes

The app requires the following ESI scopes on the Director/CEO token:

- `esi-assets.read_corporation_assets.v1`
- `esi-corporations.read_divisions.v1`
- `esi-universe.read_structures.v1`
- `esi-corporations.read_container_logs.v1`
- `esi-wallet.read_corporation_wallets.v1`

### Step 4: Run Migrations

```bash
python manage.py migrate corp_inventory
```

### Step 5: Collect Static Files

```bash
python manage.py collectstatic
```

### Step 6: Restart Services

```bash
# Systemd
supervisorctl restart myauth:

# Docker
docker compose restart
```

### Step 7: Configure Permissions

Grant permissions to users/groups in Alliance Auth admin:

| Permission | Description |
|---|---|
| `corp_inventory.basic_access` | Basic access to the app |
| `corp_inventory.view_hangar` | View corporation hangars |
| `corp_inventory.view_transactions` | View transaction logs |
| `corp_inventory.manage_tracking` | Manage hangar tracking settings |
| `corp_inventory.manage_corporations` | Add/remove tracked corporations |

### Step 8: Set Up Corporations

**Automatic Detection (Recommended)**

When a Director or CEO authenticates with Alliance Auth and adds their ESI token with the required scopes, their corporation is **automatically detected and added** to the tracking list.

**Manual Addition (Alternative)**

1. Navigate to Corp Inventory  Manage Corporations
2. Enter the corporation ID and name
3. Click Add

Or via Django admin: **Corp Inventory  Corporations  Add**.

### Step 9: Add an ESI Token

A corporation Director or CEO must authenticate with Alliance Auth and add a token with all required scopes (listed in Step 3). The app automatically finds and uses this token for syncing.

---

## Optional: EVE SDE Integration

[django-eveonline-sde](https://pypi.org/project/django-eveonline-sde/) provides a local database copy of the EVE Static Data Export. When installed, corp-inventory uses it for:

- **Type name lookups**  one bulk DB query per sync instead of one ESI call per unknown type
- **Location hierarchy** (system  constellation  region)  a single `SELECT` join instead of three serial ESI calls

Both operations fall back to ESI automatically if the SDE is not installed.

### Install

```bash
pip install "git+https://github.com/Thrainkrilleve/corp-inventory.git@v0.1.31#egg=allianceauth-corp-inventory[sde]"
```

### Configure `local.py`

`modeltranslation` must be first in `INSTALLED_APPS`:

```python
INSTALLED_APPS = ["modeltranslation"] + INSTALLED_APPS

INSTALLED_APPS += [
    "eve_sde",
]
```

### Load SDE Data

```bash
python manage.py migrate
python manage.py esde_load_sde
```

### Keep SDE Current (Celery Beat)

SDE updates are released after each EVE downtime. Add a daily check task (see the Periodic Tasks section below).

---

## Updating

### Systemd / Bare Metal

```bash
pip install --upgrade git+https://github.com/Thrainkrilleve/corp-inventory.git@v0.1.31
python manage.py migrate
python manage.py collectstatic --noinput
supervisorctl restart myauth:
```

### Docker

```bash
docker compose exec allianceauth_gunicorn bash
pip install --upgrade git+https://github.com/Thrainkrilleve/corp-inventory.git@v0.1.31
auth migrate
auth collectstatic --noinput
exit
docker compose restart
```

Update your `requirements.txt` pin:
```
allianceauth-corp-inventory @ git+https://github.com/Thrainkrilleve/corp-inventory.git@v0.1.31
```

### After Updating

1. Check [CHANGELOG.md](CHANGELOG.md) for any breaking changes
2. Visit **Corp Inventory  Diagnostics & Logs** to verify everything is working

---

## Configuration

Put these optional settings in your `local.py`:

```python
# How often to sync hangar data (in minutes, default: 30)
CORPINVENTORY_SYNC_INTERVAL = 30

# Maximum age of data before requiring refresh (in hours, default: 24)
CORPINVENTORY_DATA_MAX_AGE = 24

# Enable notifications for hangar transactions (default: True)
CORPINVENTORY_ENABLE_NOTIFICATIONS = True

# Minimum value (ISK) for transaction alerts (default: 100M)
CORPINVENTORY_ALERT_THRESHOLD = 100000000
```

## Periodic Tasks

Add to your `local.py`:

```python
from celery.schedules import crontab

CELERYBEAT_SCHEDULE["corp_inventory_sync"] = {
    "task": "corp_inventory.tasks.sync_all_corporations",
    "schedule": crontab(minute="*/30"),
}

# Only needed if using django-eveonline-sde
if "eve_sde" in INSTALLED_APPS:
    CELERYBEAT_SCHEDULE["EVE SDE :: Check for SDE Updates"] = {
        "task": "eve_sde.tasks.check_for_sde_updates",
        "schedule": crontab(minute="0", hour="12"),  # daily at 12:00 UTC
    }
```

## Theme Support

Corp Inventory adapts to Alliance Auth's theme system automatically  light/dark mode, aa-gdpr, and any Bootstrap-based custom theme are supported via CSS variables with no extra configuration required.

---

## Usage

### Automatic Syncing

Hangar data syncs on the configured interval (default every 30 minutes). A manual **Sync Now** button is available in the app for users with the `manage_tracking` permission.

### Transaction Logs

Every change detected between syncs is recorded:

| Type | Description |
|---|---|
| `ADD` | New item appeared in a hangar |
| `REMOVE` | Item left a hangar |
| `CHANGE` | Quantity changed on an existing stack |
| `MOVE` | Item moved to a different location or structure |

### Alert Rules

Configure in Django admin  **Corp Inventory  Alert Rules**. Watch for specific type IDs, value thresholds, or quantity changes, and choose which Alliance Auth users receive notifications.

---

## Troubleshooting

### Built-in Diagnostics Page

Navigate to **Corp Inventory  Diagnostics & Logs** for:

- ESI token validity per corporation
- Character authentication status
- Last sync times and item/transaction counts
- Recent log output
- Common issues with solutions

**Start here before checking anything else.**

### Viewing Logs

```bash
# Docker
docker logs -f allianceauth_beat
docker logs -f allianceauth_worker

# Systemd
journalctl -u allianceauth-beat -f
journalctl -u allianceauth-worker -f
```

### Manual Test Sync

```bash
python manage.py shell
```
```python
from corp_inventory.tasks import sync_all_corporations
sync_all_corporations()
```

### Common Issues

**No valid token found**
A Corporation Director or CEO must authenticate with Alliance Auth and add a token with all required scopes. The token must not be expired.

**No characters found**
No one from the corporation has authenticated with Alliance Auth. Have a Director/CEO log in and add their character.

**Sync completes but no items appear**
Items must be in corporation hangars (`CorpSAG1``CorpSAG7`). Items in personal hangars or containers are not tracked. Check the Diagnostics page for item counts and ESI errors.

**Missing ESI scopes**
All five scopes listed in Step 3 are required. Have the Director/CEO re-authenticate and confirm the scopes are granted.

**Static files not loading**
Run `python manage.py collectstatic` and restart your web server.

### Performance

For large inventories (10,000+ items):
- Increase `CORPINVENTORY_SYNC_INTERVAL` to reduce sync frequency
- Install the optional SDE integration to eliminate per-type ESI calls during sync
- Monitor Celery worker performance via the Diagnostics page

---

## Development

```bash
git clone https://github.com/Thrainkrilleve/corp-inventory.git
cd allianceauth-corp-inventory
pip install -e .[dev]
pre-commit install
```

### Running Tests

```bash
python runtests.py
```

### Code Style

- **Black**  code formatting
- **isort**  import sorting
- **flake8**  linting

---

## Contributing

Contributions are welcome. Fork the repo, create a feature branch, and open a pull request.

## License

MIT  see [LICENSE](LICENSE).

## Credits

- Built for [Alliance Auth](https://gitlab.com/allianceauth/allianceauth)
- EVE Online and the EVE logo are registered trademarks of CCP hf.

## Support

[GitHub Issues](https://github.com/Thrainkrilleve/corp-inventory/issues)
