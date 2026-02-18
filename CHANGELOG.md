# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/yourusername/allianceauth-corp-inventory/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/allianceauth-corp-inventory/releases/tag/v0.1.0
