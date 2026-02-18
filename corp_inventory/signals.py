"""
Signals for Corp Inventory
Automatically adds corporations when characters authenticate via ESI
"""

import logging

from django.dispatch import receiver
from django.db.models.signals import post_save
from allianceauth.eveonline.models import EveCharacter

from .models import Corporation

logger = logging.getLogger(__name__)


@receiver(post_save, sender=EveCharacter)
def auto_add_corporation(sender, instance, created, **kwargs):
    """
    Automatically add a corporation when a new character is authenticated.
    This happens when a Director/CEO character adds their ESI token.
    
    Args:
        sender: The model that triggered the signal (EveCharacter)
        instance: The EveCharacter instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if not created:
        return  # Only process new character additions
    
    if not instance.character_corporation_id:
        logger.debug(f"Character {instance.character_name} has no corporation ID")
        return
    
    try:
        # Check if corporation is already being tracked
        corporation, created = Corporation.objects.get_or_create(
            corporation_id=instance.character_corporation_id,
            defaults={
                'corporation_name': instance.corporation_name,
                'tracking_enabled': True,
            }
        )
        
        if created:
            logger.info(
                f"Auto-added corporation {instance.corporation_name} "
                f"(ID: {instance.character_corporation_id}) "
                f"when {instance.character_name} authenticated"
            )
        else:
            # Corporation already exists, just ensure it has the name
            if not corporation.corporation_name or corporation.corporation_name == "Unknown":
                corporation.corporation_name = instance.corporation_name
                corporation.save(update_fields=['corporation_name'])
                logger.info(
                    f"Updated corporation name for {corporation.corporation_id} "
                    f"to {instance.corporation_name}"
                )
    
    except Exception as e:
        logger.error(
            f"Error auto-adding corporation for character {instance.character_name}: {e}",
            exc_info=True
        )
