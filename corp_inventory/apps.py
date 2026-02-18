from django.apps import AppConfig


class CorpInventoryConfig(AppConfig):
    name = "corp_inventory"
    label = "corp_inventory"
    verbose_name = "Corp Inventory"
    
    def ready(self):
        """Register signal handlers and admin"""
        import corp_inventory.signals  # noqa: F401
        import corp_inventory.admin  # noqa: F401
