# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.23] - 2026-02-18

### Fixed
- **Container logs page now reachable** — added "Container Logs" navigation button to the hangar page; the page existed but had no link from anywhere in the UI
- **Container logs: partial pages no longer discarded on network error** — if ESI DNS or connection fails mid-pagination (e.g. page 3 of 4), records already fetched from pages 1-2 are now saved instead of being thrown away and returning an empty result

## [0.1.22] - 2026-02-18

### Performance
- **Market prices cached in Redis for 2 hours** — `PriceManager.get_market_prices()` was downloading ~40,000 ESI price records on *every* sync run (every 30 min). Now fetched once and cached; subsequent syncs serve from Redis instantly
- **Type-name lookups: DB first, ESI only for new types** — previously made one ESI HTTP call per unique item type in the hangar on every sync (could be 500–1000+ calls). Now queries existing `HangarItem` records for known type names; ESI is only called for types never seen before
- **Bulk DB writes in `process_assets`** — replaced per-item `save()` / `create()` / individual `create_transaction()` calls with `bulk_update`, `bulk_create`, and batched `bulk_create` for transactions. Reduces DB round-trips from O(N items) to O(1) per sync
- **Divisions prefetched** — eliminated per-asset `HangarDivision.objects.filter().first()` query inside the loop; division map now loaded once before processing
- **`HangarSnapshot.snapshot_data` no longer stores full JSON blobs** — the field was duplicating all `HangarItem` data on every sync row, growing indefinitely. New syncs write `{}`. Migration 0006 clears existing blobs
- **Alert task skipped when no rules exist** — `process_alert_rules` task is no longer dispatched if the corporation has zero active alert rules
- **Daily cleanup task** (`cleanup_old_data`) registered in Celery Beat — keeps last 48 snapshots per corp (24 h), deletes transactions older than 90 days

## [0.1.21] - 2026-02-18

### Fixed
- `sync_corporation` view was gated by `manage_tracking` only; users with `manage_corporations` who click Sync Now received a 403. Now accepts either `manage_corporations` **or** `manage_tracking`
- All 6 non-Corporation models lacked `default_permissions = ()`, causing Django to auto-create 28 unused CRUD permissions (`add_hangardivision`, `view_location`, etc.) that cluttered the AA permission picker
- Migration 0005: data migration removes those 28 spurious permissions from existing installs

## [0.1.20] - 2026-02-18

### Fixed
- Wallet and ISK totals on dashboard displaying as `6.00 ISK` / `6.90 ISK`: base.html jQuery `.isk-value` handler called `parseFloat()` on already-formatted Python strings (`"6.90B ISK"` → `6.9`; `"6,900,450,319 ISK"` → `6` due to comma). Fix: skip elements whose text already contains `B/M/T/K` or commas; strip trailing ` ISK` suffix before parsing raw numeric elements
- `__init__.py` version not bumped in sync with `pyproject.toml`
- Manage Corporations page: wallet balance shown as raw decimal (e.g. `2489682759.95 ISK`) with no comma separators; promoted `isk_abbrev()`/`isk_full()` helpers to module level and annotated corp objects with `wallet_display` in the view

## [0.1.19] - 2026-02-18

### Fixed
- CSS dark/light theme: strip all `background-color` from custom classes; wrap surfaces in Bootstrap `.panel.panel-default` / `.well` components so AA themes apply correctly across all AA versions (Bootstrap 5.3+ CSS vars like `--bs-secondary-bg` are not available in all AA4 installs)
- Dashboard ISK display: compute `isk_abbrev()` and `isk_full()` in Python to avoid Django template filter order bug (`intcomma` stringifies before `floatformat` can act)
- Migration 0004: consolidate `unique_together` and `indexes` into `CreateModel` options block to fix MySQL errno 150 FK constraint error

## [0.1.13] - 2026-02-17

### Fixed
- Remove `ticker` field references from views - Corporation model has no ticker field

## [0.1.12] - 2026-02-17

### Fixed
- After adding ESI token, auto-detect character's corporation, register it for tracking, and trigger an immediate sync

## [0.1.11] - 2026-02-17

### Changed
- Replace ESI token URL detection with a proper `add_corp_token` view using `@token_required` decorator for direct EVE SSO flow

## [0.1.10] - 2026-02-17

### Fixed
- Commit template fix: use dynamic `{{ esi_token_url }}` in manage_corporations.html
- Fix ESI token URL flow to only use fallback when all auto-detection attempts fail
## [0.1.10] - 2026-02-17

### Fixed
- Fix hardcoded `/auth/eveauth/` URL in manage_corporations.html template to use dynamic `{{ esi_token_url }}`

## [0.1.9] - 2026-02-17

### Fixed
- Remove unused CORPINVENTORY_ESI_TOKEN_URL from app_settings.py (now uses auto-detection in views.py)

## [0.1.8] - 2026-02-17

### Fixed
- Fix ESI token URL detection logic to properly auto-detect `authentication:token_management` instead of using fallback

## [0.1.7] - 2026-02-17

### Fixed
- Use `authentication:token_management` URL for ESI token management in Alliance Auth

## [0.1.6] - 2026-02-17

### Fixed
- Resolve ESI token add URL using `authentication:add_character` for Alliance Auth 3.x+ installations

## [0.1.5] - 2026-02-17

### Fixed
- Resolve ESI token add URL using the Alliance Auth `esi` namespace when available

## [0.1.4] - 2026-02-17

### Fixed
- Avoid AttributeError when `CORPINVENTORY_ESI_TOKEN_URL` is missing during mixed-version installs

## [0.1.3] - 2026-02-17

### Fixed
- Align default auto field and explicit index names with initial migrations to stop repeated makemigrations prompts

## [0.1.2] - 2026-02-17

### Added
- Automatic corporation detection and tracking when characters authenticate via ESI
- Signal handler that adds corporations to tracking list when new Director/CEO characters authenticate
- Theme-aware styling that automatically adapts to the user's selected Alliance Auth theme (light/dark modes)
- Support for aa-gdpr theme module and other custom Alliance Auth themes
- `fix_corp_inventory_migration` management command to automatically resolve migration history conflicts
- EVE SSO token link on Manage Corporations page
- Diagnostics command for sync troubleshooting

### Changed
- Redesigned CSS to use Bootstrap CSS variables for theme compatibility
- Removed all hardcoded colors in favor of theme-aware color system
- Updated templates to use CSS classes instead of inline styles for better maintainability
- Resolve ESI token add URL via URL reverse for Alliance Auth compatibility

### Fixed
- Migration history conflicts from earlier versions now automatically resolved (no more index rename errors)
- AppConfig default selection for Django 4 to register URL hooks without long app label

## [0.1.1] - 2026-02-17

### Added
- Comprehensive diagnostics page at `/corp-inventory/logs/` for troubleshooting
- Token validation and character count display in logs page
- Item and transaction count display in logs page
- Recent log entries viewer (last 100 lines) in diagnostics page
- Manual sync trigger instructions in diagnostics page

### Changed
- Enhanced `sync_corporation_hangar()` task to return status dictionary with status, message, and asset count
- Improved logs page with detailed diagnostic information
- Updated README with comprehensive installation, update, and troubleshooting guides

### Fixed
- Migration initial field names (division_id and division_name) to match model definitions
- Missing ESI scope `esi-universe.read_structures.v1` added to operations

## [0.1.0] - 2026-02-17

### Added
- Initial release of Corp Inventory
- Corporation hangar tracking and monitoring
- Real-time inventory viewing with search and filters
- Transaction logging for additions, removals, and changes
- Support for multiple locations (stations and structures)
- Division-based filtering
- Automatic ISK valuation of hangar contents
- Alert rules for custom notifications
- Transaction history and audit logs
- Statistics dashboard with analytics
- ESI integration for data fetching
- Celery tasks for automated syncing
- Admin interface for managing corporations and settings
- Full permission system for access control
- Mobile-responsive templates

### Features
- Track items across multiple corporation hangars
- Monitor who adds/removes items
- Automatic value estimation
- Customizable alert rules
- Historical transaction data
- Location-based inventory views
- Division filtering
- Search functionality

[Unreleased]: https://github.com/yourusername/allianceauth-corp-inventory/compare/v0.1.5...HEAD
[0.1.5]: https://github.com/yourusername/allianceauth-corp-inventory/releases/tag/v0.1.5
[0.1.4]: https://github.com/yourusername/allianceauth-corp-inventory/releases/tag/v0.1.4
[0.1.3]: https://github.com/yourusername/allianceauth-corp-inventory/releases/tag/v0.1.3
[0.1.2]: https://github.com/yourusername/allianceauth-corp-inventory/releases/tag/v0.1.2
[0.1.1]: https://github.com/yourusername/allianceauth-corp-inventory/releases/tag/v0.1.1
[0.1.0]: https://github.com/yourusername/allianceauth-corp-inventory/releases/tag/v0.1.0
