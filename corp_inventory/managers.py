"""
ESI API Manager for Corp Inventory
Handles all ESI API calls for fetching corporation hangar data
"""

import logging
from typing import Dict, List, Optional

from esi.clients import EsiClientProvider
from esi.models import Token

logger = logging.getLogger(__name__)

esi = EsiClientProvider()


class CorpInventoryManager:
    """
    Manages ESI API calls for corporation inventory
    """
    
    @staticmethod
    def get_corporation_assets(token: Token, corporation_id: int) -> List[Dict]:
        """
        Fetch all assets for a corporation
        
        Args:
            token: ESI token with required scopes
            corporation_id: Corporation ID
            
        Returns:
            List of asset dictionaries
        """
        try:
            client = esi.client
            assets = client.Assets.get_corporations_corporation_id_assets(
                corporation_id=corporation_id,
                token=token.valid_access_token()
            ).results()
            
            logger.info(
                f"Retrieved {len(assets)} assets for corporation {corporation_id}"
            )
            return assets
            
        except Exception as e:
            logger.error(
                f"Error fetching assets for corporation {corporation_id}: {e}"
            )
            return []
    
    @staticmethod
    def get_corporation_divisions(token: Token, corporation_id: int) -> Dict:
        """
        Fetch corporation divisions
        
        Args:
            token: ESI token with required scopes
            corporation_id: Corporation ID
            
        Returns:
            Dictionary with division information
        """
        try:
            client = esi.client
            divisions = client.Corporation.get_corporations_corporation_id_divisions(
                corporation_id=corporation_id,
                token=token.valid_access_token()
            ).results()
            
            logger.info(
                f"Retrieved divisions for corporation {corporation_id}"
            )
            return divisions
            
        except Exception as e:
            logger.error(
                f"Error fetching divisions for corporation {corporation_id}: {e}"
            )
            return {}
    
    @staticmethod
    def get_structure_info(token: Token, structure_id: int) -> Optional[Dict]:
        """
        Fetch structure information
        
        Args:
            token: ESI token
            structure_id: Structure ID
            
        Returns:
            Structure information dictionary or None
        """
        try:
            client = esi.client
            structure = client.Universe.get_universe_structures_structure_id(
                structure_id=structure_id,
                token=token.valid_access_token()
            ).results()
            
            return structure
            
        except Exception as e:
            logger.warning(
                f"Error fetching structure {structure_id}: {e}"
            )
            return None
    
    @staticmethod
    def get_station_info(station_id: int) -> Optional[Dict]:
        """
        Fetch station information (no auth required)
        
        Args:
            station_id: Station ID
            
        Returns:
            Station information dictionary or None
        """
        try:
            client = esi.client
            station = client.Universe.get_universe_stations_station_id(
                station_id=station_id
            ).results()
            
            return station
            
        except Exception as e:
            logger.warning(
                f"Error fetching station {station_id}: {e}"
            )
            return None
    
    @staticmethod
    def get_type_info(type_id: int) -> Optional[Dict]:
        """
        Fetch type information
        
        Args:
            type_id: Type ID
            
        Returns:
            Type information dictionary or None
        """
        try:
            client = esi.client
            type_info = client.Universe.get_universe_types_type_id(
                type_id=type_id
            ).results()
            
            return type_info
            
        except Exception as e:
            logger.warning(
                f"Error fetching type {type_id}: {e}"
            )
            return None
    
    @staticmethod
    def get_solar_system_info(system_id: int) -> Optional[Dict]:
        """
        Fetch solar system information
        
        Args:
            system_id: Solar system ID
            
        Returns:
            Solar system information dictionary or None
        """
        try:
            client = esi.client
            system = client.Universe.get_universe_systems_system_id(
                system_id=system_id
            ).results()
            
            return system
            
        except Exception as e:
            logger.warning(
                f"Error fetching system {system_id}: {e}"
            )
            return None
    
    @staticmethod
    def get_constellation_info(constellation_id: int) -> Optional[Dict]:
        """
        Fetch constellation information
        
        Args:
            constellation_id: Constellation ID
            
        Returns:
            Constellation information dictionary or None
        """
        try:
            client = esi.client
            constellation = client.Universe.get_universe_constellations_constellation_id(
                constellation_id=constellation_id
            ).results()
            
            return constellation
            
        except Exception as e:
            logger.warning(
                f"Error fetching constellation {constellation_id}: {e}"
            )
            return None
    
    @staticmethod
    def get_region_info(region_id: int) -> Optional[Dict]:
        """
        Fetch region information
        
        Args:
            region_id: Region ID
            
        Returns:
            Region information dictionary or None
        """
        try:
            client = esi.client
            region = client.Universe.get_universe_regions_region_id(
                region_id=region_id
            ).results()
            
            return region
            
        except Exception as e:
            logger.warning(
                f"Error fetching region {region_id}: {e}"
            )
            return None


    @staticmethod
    def get_corporation_wallets(token: Token, corporation_id: int) -> List[Dict]:
        """
        Fetch corporation wallet balances.

        Requires scope: esi-wallet.read_corporation_wallets.v1

        Args:
            token: ESI token with required scopes
            corporation_id: Corporation ID

        Returns:
            List of wallet dicts, each with 'division' (1-7) and 'balance' (float)
        """
        try:
            client = esi.client
            wallets = client.Wallet.get_corporations_corporation_id_wallets(
                corporation_id=corporation_id,
                token=token.valid_access_token()
            ).results()
            logger.info(
                f"Retrieved {len(wallets)} wallet divisions for corporation {corporation_id}"
            )
            return wallets
        except Exception as e:
            logger.error(
                f"Error fetching wallets for corporation {corporation_id}: {e}"
            )
            return []


class PriceManager:
    """
    Manages market price lookups for valuation
    """
    
    @staticmethod
    def get_market_prices() -> Dict[int, float]:
        """
        Fetch current market prices for all items
        
        Returns:
            Dictionary mapping type_id to price
        """
        try:
            client = esi.client
            prices = client.Market.get_markets_prices().results()
            
            price_dict = {}
            for item in prices:
                if "average_price" in item:
                    price_dict[item["type_id"]] = item["average_price"]
                elif "adjusted_price" in item:
                    price_dict[item["type_id"]] = item["adjusted_price"]
            
            logger.info(f"Retrieved prices for {len(price_dict)} items")
            return price_dict
            
        except Exception as e:
            logger.error(f"Error fetching market prices: {e}")
            return {}
