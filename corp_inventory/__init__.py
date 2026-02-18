"""Initialize the app"""

__version__ = "0.1.9"
__title__ = "Corp Inventory"
__package_name__ = "allianceauth-corp-inventory"
__app_name__ = "corp_inventory"
__esi_compatibility_date__ = "2026-02-17"
__app_name_useragent__ = "AA-Corp-Inventory"
__github_url__ = f"https://github.com/Thrainkrilleve/corp-inventory"

__character_operations__ = []

__corporation_operations__ = [
    "GetCorporationsCorporationIdAssets",
    "GetCorporationsCorporationIdDivisions",
]

__universe_operations__ = [
    "GetUniverseStructuresStructureId",
    "GetUniverseStationsStationId",
    "GetUniverseSystemsSystemId",
    "GetUniverseConstellationsConstellationId",
    "GetUniverseRegionsRegionId",
    "GetUniverseTypesTypeId",
]

