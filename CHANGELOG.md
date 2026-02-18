# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
