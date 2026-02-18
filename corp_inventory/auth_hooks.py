"""
Auth hooks for Corp Inventory
"""

from django.utils.translation import gettext_lazy as _

from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

from . import urls


class CorpInventoryMenuItem(MenuItemHook):
    """
    This class ensures only authorized users will see the menu entry
    """
    
    def __init__(self):
        # Setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _("Corp Inventory"),
            "fas fa-warehouse fa-fw",
            "corp_inventory:index",
            navactive=["corp_inventory:"],
        )
    
    def render(self, request):
        if request.user.has_perm("corp_inventory.basic_access"):
            return MenuItemHook.render(self, request)
        return ""


@hooks.register("menu_item_hook")
def register_menu():
    return CorpInventoryMenuItem()


@hooks.register("url_hook")
def register_urls():
    return UrlHook(urls, "corp_inventory", r"^corp_inventory/")
