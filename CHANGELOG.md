# Changelog

All notable changes to this project will be documented in this file.

---

## [0.1.29] - 2026-02-21

### Added
- **MOVE transaction detection**  the app now records a MOVE transaction when it detects that an existing item has changed location between syncs (e.g. items transferred to a different station or structure). Previously the MOVE type existed in the model but was never written.

### Fixed
- **Unknown locations are now retried on every sync**  previously, if a structure could not be resolved via ESI (e.g. 403 Forbidden, structure reinforced, or assets in safety), the "Unknown Location" placeholder was cached permanently and never re-attempted. The location record is now updated in-place as soon as ESI returns valid data, preserving all existing item links.
- **Clearer 403 logging for inaccessible structures**  structure ESI failures due to HTTP 403 now log a specific message explaining the cause (no docking access, destroyed structure, or asset safety) rather than a raw exception.

---

## [0.1.28] - 2026-02-21

### Fixed
- **Dark mode card and code block colours**  the aa-gdpr Flatly dark theme sets `--bs-body-bg` to a dark value but does not activate Bootstrap's native dark-mode component variables, leaving card backgrounds and `<pre>` code blocks white-on-white. All affected surfaces now explicitly use `--bs-body-bg` and `--bs-body-color` to stay consistent with the active theme.
- **Form label visibility**  labels on the Manage Corporations page were invisible in dark mode because they lacked Bootstrap's `form-label` class.

---

## [0.1.27] - 2026-02-21

### Fixed
- **Stat cards no longer override theme colours**  the `.stat-card` class had a hardcoded `background-color: var(--bs-secondary-bg, #fff)` fallback that forced a white background regardless of the active theme. The override has been removed so cards inherit the theme naturally.

---

## [0.1.26] - 2026-02-21

### Fixed
- **Container logs were always empty**  the ESI field for the acting character is `character_id`, but the code was reading `logged_by`, which always returned `None` and caused every log entry to be skipped. All container logs now populate correctly.

---

## [0.1.25] - 2026-02-21

### Changed
- **Alliance Auth v4 template system**  templates now extend `allianceauth/base-bs5.html` instead of the legacy Bootstrap 3 base, wiring into AA v4's ThemeHook system so installed themes are applied correctly. DataTables has been updated to the bundled v2 API.

---

## [0.1.24] - 2026-02-21

### Changed
- **Bootstrap 3 to Bootstrap 5 migration**  all templates, CSS, and JavaScript updated to Bootstrap 5. Removed deprecated BS3 component classes, updated all data attributes, modals, alerts, and tooltips to BS5 equivalents.

---

## [0.1.23] - 2026-02-18

### Fixed
- **Container Logs page was unreachable**  the page existed but had no navigation link; a "Container Logs" button has been added to the hangar view.
- **Partial ESI pages no longer discarded**  if an ESI network error occurs mid-pagination, log entries already fetched from earlier pages are now saved rather than silently dropped.

---

## [0.1.22] - 2026-02-18

### Performance
- **Sync speed dramatically improved**  market prices are now cached in Redis for 2 hours instead of re-fetching ~40,000 records every sync. Item type names are looked up in the database first and only fetched from ESI for types never seen before, cutting ESI calls from hundreds per sync to near zero for established corps.
- **Bulk database writes**  all HangarItem creates, updates, and transaction inserts are now done with bulk_create/bulk_update instead of per-row saves, reducing database round-trips from O(N) to O(1).
- **Automatic data pruning**  a daily cleanup task keeps the last 48 snapshots per corporation and deletes transactions older than 90 days to control database growth.

---

## [0.1.21] - 2026-02-18

### Fixed
- **Sync Now returned 403 for some users**  the sync view required `manage_tracking` but users with only `manage_corporations` were also expected to be able to trigger syncs. Both permissions are now accepted.
- **Spurious Django permissions removed**  28 auto-generated CRUD permissions (add_hangardivision, view_location, etc.) were cluttering the Alliance Auth permission picker. These have been removed via a data migration.

---

## [0.1.20] - 2026-02-18

### Fixed
- **ISK values displayed incorrectly on dashboard**  large formatted values like `6.90B ISK` were being re-parsed by the JavaScript formatter and collapsed to `6.00 ISK`. The formatter now skips already-formatted values and the Manage Corporations wallet balance is displayed with correct comma separators.

---

## [0.1.19] - 2026-02-18

### Fixed
- **Dark/light theme compatibility**  removed all hardcoded background colours from custom CSS classes so Alliance Auth themes apply correctly. Fixed a Django template filter ordering bug that caused ISK values to render incorrectly. Resolved a MySQL FK constraint error in migration 0004.

---

## [0.1.12] - 2026-02-17

### Added
- **Automatic corporation registration**  when a Director or CEO authenticates via ESI, their corporation is automatically detected, registered for tracking, and an initial sync is triggered without any manual setup.

---

## [0.1.1] - 2026-02-17

### Added
- **Diagnostics page**  a built-in diagnostics view at /corp-inventory/logs/ shows ESI token status, character counts, item and transaction counts, recent log output, and common troubleshooting steps in one place.

---

## [0.1.0] - 2026-02-17

### Added
- Initial release. Corporation hangar tracking, transaction logging, multi-location support, division filtering, ISK valuation, alert rules, statistics dashboard, and ESI integration via Celery background tasks.

---

[0.1.29]: https://github.com/Thrainkrilleve/corp-inventory/releases/tag/v0.1.29
[0.1.28]: https://github.com/Thrainkrilleve/corp-inventory/releases/tag/v0.1.28
[0.1.27]: https://github.com/Thrainkrilleve/corp-inventory/releases/tag/v0.1.27
[0.1.26]: https://github.com/Thrainkrilleve/corp-inventory/releases/tag/v0.1.26
[0.1.25]: https://github.com/Thrainkrilleve/corp-inventory/releases/tag/v0.1.25
[0.1.24]: https://github.com/Thrainkrilleve/corp-inventory/releases/tag/v0.1.24
[0.1.23]: https://github.com/Thrainkrilleve/corp-inventory/releases/tag/v0.1.23
[0.1.22]: https://github.com/Thrainkrilleve/corp-inventory/releases/tag/v0.1.22
[0.1.21]: https://github.com/Thrainkrilleve/corp-inventory/releases/tag/v0.1.21
[0.1.20]: https://github.com/Thrainkrilleve/corp-inventory/releases/tag/v0.1.20
[0.1.19]: https://github.com/Thrainkrilleve/corp-inventory/releases/tag/v0.1.19
[0.1.12]: https://github.com/Thrainkrilleve/corp-inventory/releases/tag/v0.1.12
[0.1.1]: https://github.com/Thrainkrilleve/corp-inventory/releases/tag/v0.1.1
[0.1.0]: https://github.com/Thrainkrilleve/corp-inventory/releases/tag/v0.1.0
