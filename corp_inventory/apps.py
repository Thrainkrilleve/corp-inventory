from django.apps import AppConfig


class CorpInventoryConfig(AppConfig):
    name = "corp_inventory"
    label = "corp_inventory"
    verbose_name = "Corp Inventory"
    
    def ready(self):
        """Register signal handlers"""
        import corp_inventory.signals  # noqa: F401
