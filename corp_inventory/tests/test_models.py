"""
Basic tests for Corp Inventory
"""

from django.test import TestCase
from django.contrib.auth.models import User
from corp_inventory.models import Corporation, HangarItem, Location


class CorporationModelTest(TestCase):
    """Test Corporation model"""
    
    def setUp(self):
        """Set up test data"""
        self.corporation = Corporation.objects.create(
            corporation_id=123456789,
            corporation_name="Test Corp",
            tracking_enabled=True
        )
    
    def test_corporation_creation(self):
        """Test corporation can be created"""
        self.assertEqual(self.corporation.corporation_name, "Test Corp")
        self.assertEqual(self.corporation.corporation_id, 123456789)
        self.assertTrue(self.corporation.tracking_enabled)
    
    def test_corporation_string_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.corporation), "Test Corp")


class LocationModelTest(TestCase):
    """Test Location model"""
    
    def setUp(self):
        """Set up test data"""
        self.location = Location.objects.create(
            location_id=60003760,
            location_name="Jita IV - Moon 4 - Caldari Navy Assembly Plant",
            location_type="station",
            solar_system_id=30000142,
            solar_system_name="Jita"
        )
    
    def test_location_creation(self):
        """Test location can be created"""
        self.assertEqual(self.location.location_id, 60003760)
        self.assertEqual(self.location.location_type, "station")
        self.assertEqual(self.location.solar_system_name, "Jita")
    
    def test_location_string_representation(self):
        """Test string representation"""
        self.assertIn("Jita", str(self.location))


class HangarItemModelTest(TestCase):
    """Test HangarItem model"""
    
    def setUp(self):
        """Set up test data"""
        self.corporation = Corporation.objects.create(
            corporation_id=123456789,
            corporation_name="Test Corp",
            tracking_enabled=True
        )
        
        self.location = Location.objects.create(
            location_id=60003760,
            location_name="Test Station",
            location_type="station"
        )
        
        self.item = HangarItem.objects.create(
            corporation=self.corporation,
            item_id=9876543210,
            type_id=34,  # Tritanium
            type_name="Tritanium",
            location=self.location,
            quantity=1000000,
            estimated_value=5000000.00,
            is_active=True
        )
    
    def test_item_creation(self):
        """Test hangar item can be created"""
        self.assertEqual(self.item.type_name, "Tritanium")
        self.assertEqual(self.item.quantity, 1000000)
        self.assertTrue(self.item.is_active)
    
    def test_item_relationships(self):
        """Test item relationships"""
        self.assertEqual(self.item.corporation, self.corporation)
        self.assertEqual(self.item.location, self.location)
