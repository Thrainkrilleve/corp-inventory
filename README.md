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

### Step 1: Install the Package

```bash
pip install allianceauth-corp-inventory
```

### Step 2: Configure Alliance Auth

Add `corp_inventory` to your `INSTALLED_APPS` in your Alliance Auth `local.py` settings file:

```python
INSTALLED_APPS = [
    # ... other apps
    'corp_inventory',
]
```

### Step 3: Configure ESI Scopes

The app requires the following ESI scopes:
- `esi-assets.read_corporation_assets.v1`
- `esi-corporations.read_divisions.v1`

These scopes must be added to your Alliance Auth ESI application.

### Step 4: Run Migrations

```bash
python manage.py migrate corp_inventory
```

### Step 5: Collect Static Files

```bash
python manage.py collectstatic
```

### Step 6: Restart Services

Restart your Alliance Auth supervisord and celery services.

### Step 7: Configure Permissions

Grant permissions to users/groups:

- `corp_inventory.basic_access` - Basic access to the app
- `corp_inventory.view_hangar` - View corporation hangars
- `corp_inventory.view_transactions` - View transaction logs
- `corp_inventory.manage_tracking` - Manage hangar tracking settings

### Step 8: Set Up Corporations

1. Log in to Django admin
2. Navigate to Corp Inventory → Corporations
3. Add your corporation(s) to track
4. Enable tracking for each corporation

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

The main task `sync_all_corporations` runs based on the `CORPINVENTORY_SYNC_INTERVAL` setting.

## Troubleshooting

### No data appearing

1. Verify ESI scopes are correctly configured
2. Check that a valid token exists for the corporation
3. Manually trigger a sync from the web interface
4. Check Celery logs for any errors

### Token issues

Make sure corporation directors have authenticated with Alliance Auth and their tokens have the required ESI scopes.

### Performance

For large inventories (10,000+ items), consider:
- Increasing the sync interval
- Adding database indexes
- Using Django's cache framework

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
