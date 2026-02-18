# Corp Inventory - Quick Reference

Quick reference guide for using Alliance Auth Corp Inventory.

## Main Features

### Dashboard
- View all tracked corporations
- See total item counts and values
- Check last sync times
- Quick access to hangar and transaction views

### Hangar View
View all items in a corporation's hangars with:
- **Filters**: Division, location, item name
- **Information**: Quantity, location, value, last seen
- **Actions**: View details, sync manually

### Transaction Log
Track all hangar changes:
- **Addition**: Items added to hangars (green)
- **Removal**: Items removed from hangars (red)
- **Change**: Quantity changes (yellow)
- **Movement**: Items moved between locations

### Statistics
- Top items by value
- Transaction summaries
- Active alert rules
- Historical trends

## Permissions

| Permission | Description |
|------------|-------------|
| `basic_access` | Access the app |
| `view_hangar` | View corporation hangars |
| `view_transactions` | View transaction logs |
| `manage_tracking` | Manage tracking and sync |

## Common Tasks

### View Corporation Hangar
1. Corp Inventory menu → Dashboard
2. Click "View Hangar" on corporation card
3. Use filters to narrow down items

### Check Recent Transactions
1. Corp Inventory menu → Dashboard
2. Click "Transactions" on corporation card
3. Filter by type, time period, or item

### Manually Sync
1. Navigate to corporation hangar
2. Click "Sync Now" button (requires `manage_tracking` permission)
3. Wait for sync to complete (may take a few minutes)

### Search for Items
1. Go to corporation hangar
2. Enter item name in search box
3. Click "Filter"

### Filter by Location
1. Go to corporation hangar
2. Select location from dropdown
3. Click "Filter"

### View Item History
1. Find item in hangar view
2. Click "Details" button
3. View full transaction history

### View All Items at Location
1. Click location name in hangar view
2. See all corporation items at that location

## Alert Rules

Create custom alerts in Django Admin:

1. **Item Added**: Notify when specific items are added
2. **Item Removed**: Notify when items are removed
3. **Value Threshold**: Alert on high-value transactions
4. **Quantity Change**: Track quantity changes

## API Endpoints

For developers/integrations:

- `GET /corp_inventory/api/hangar/<corp_id>/` - Get hangar data as JSON

## Keyboard Shortcuts

- Use browser search (Ctrl+F / Cmd+F) to find items quickly in tables

## Tips & Tricks

### Performance
- Use filters to reduce data displayed
- Regular syncs keep data fresh
- Check sync status on dashboard

### Monitoring
- Set up alert rules for high-value items
- Review transaction log regularly
- Check statistics for unusual activity

### Troubleshooting
- If data seems old, check last sync time
- Manually sync if needed
- Verify ESI tokens are valid

## Column Descriptions

### Hangar View
- **Item**: Item name with icon
- **Quantity**: Number of items in stack
- **Location**: Station or structure name
- **Division**: Hangar division (if applicable)
- **Estimated Value**: ISK value based on market prices
- **Last Seen**: When item was last detected in sync

### Transaction Log
- **Time**: When change was detected
- **Type**: Addition/Removal/Change/Movement
- **Item**: Item name with icon
- **Change**: Quantity change (+ or -)
- **Location**: Where transaction occurred
- **Division**: Hangar division
- **Value**: Estimated ISK value of transaction

## Color Coding

- **Green**: Additions, positive values
- **Red**: Removals, negative values
- **Yellow**: Changes, warnings
- **Blue**: Information, active items

## Data Freshness

- Automatic sync runs every 30 minutes (configurable)
- Manual sync available for immediate updates
- Last sync time shown on dashboard
- Data max age: 24 hours (configurable)

## ESI Scopes Required

The app needs these scopes from corporation directors:
- `esi-assets.read_corporation_assets.v1`
- `esi-corporations.read_divisions.v1`

## Storage Locations

The app tracks items in:
- **Stations**: NPC stations
- **Structures**: Player-owned structures
- **Multiple Locations**: Across New Eden

## Divisions

Corporation hangars have 7 divisions:
1. Division 1 (Hangar 1)
2. Division 2 (Hangar 2)
3. Division 3 (Hangar 3)
4. Division 4 (Hangar 4)
5. Division 5 (Hangar 5)
6. Division 6 (Hangar 6)
7. Division 7 (Hangar 7)

Custom names can be set in-game and will sync.

## Support

**Can't see menu item?**
- Check you have `basic_access` permission

**No data showing?**
- Verify corporation is enabled for tracking
- Check valid ESI token exists
- Manually trigger sync
- Check Celery logs for errors

**Transactions not appearing?**
- Wait for next sync cycle
- Manually sync
- Check sync completed successfully

**Values seem wrong?**
- Values based on market average prices
- Prices update with each sync
- Blueprint copies valued differently

## Best Practices

1. **Regular monitoring**: Check dashboard weekly
2. **Alert rules**: Set up for valuable items
3. **Permissions**: Grant appropriately to avoid data leaks
4. **Sync frequency**: Balance between freshness and server load
5. **Documentation**: Note important transactions

## Limitations

- Cannot detect *who* made changes (ESI limitation)
- Sync interval means slight delay in updates
- Market values are estimates
- Requires corporation director ESI token
- Only tracks hangar items (not containers, ships, etc.)

## Future Features

Planned enhancements:
- Export data to CSV
- Charts and graphs
- Email notifications
- Mobile app
- API improvements
- Container tracking

## Quick Links

- [Full Documentation](README.md)
- [Installation Guide](INSTALL.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
