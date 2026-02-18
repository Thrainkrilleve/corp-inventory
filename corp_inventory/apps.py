from django.apps import AppConfig


class CorpInventoryConfig(AppConfig):
    name = "corp_inventory"
    label = "corp_inventory"
    verbose_name = "Corp Inventory"
    default = True
    default_auto_field = "django.db.models.BigAutoField"
    
    def ready(self):
        """Register signal handlers, admin, and hooks"""
        import corp_inventory.signals  # noqa: F401
        import corp_inventory.admin  # noqa: F401
        import corp_inventory.auth_hooks  # noqa: F401
