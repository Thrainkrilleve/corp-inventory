"""
Diagnostic command for troubleshooting Corp Inventory sync issues
"""

import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from esi.models import Token

from corp_inventory.models import Corporation
from corp_inventory import app_settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Diagnose sync issues with Corp Inventory"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=== Corp Inventory Sync Diagnostic ===\n"))
        
        # Check 1: Corporations configured
        self.check_corporations()
        
        # Check 2: Characters in corporations
        self.check_characters()
        
        # Check 3: ESI tokens
        self.check_tokens()
        
        # Check 4: ESI connectivity
        self.check_esi_connectivity()
        
        # Check 5: Celery Beat configuration
        self.check_celery_beat()
        
    def check_corporations(self):
        """Check if corporations are configured"""
        self.stdout.write("\n[1] CORPORATIONS")
        self.stdout.write("-" * 50)
        
        corps = Corporation.objects.all()
        
        if not corps.exists():
            self.stdout.write(self.style.ERROR("✗ No corporations found!"))
            self.stdout.write("  → You must add at least one corporation in Django admin")
            self.stdout.write("  → Or have a Director/CEO authenticate to trigger auto-detection")
            return
        
        self.stdout.write(self.style.SUCCESS(f"✓ Found {corps.count()} corporation(s)"))
        
        for corp in corps:
            status = "ENABLED" if corp.tracking_enabled else "DISABLED"
            last_sync = corp.last_sync or "Never"
            self.stdout.write(f"  • {corp.corporation_name} (ID: {corp.corporation_id})")
            self.stdout.write(f"    - Status: {status}")
            self.stdout.write(f"    - Last Sync: {last_sync}")
    
    def check_characters(self):
        """Check for characters in corporations"""
        self.stdout.write("\n[2] CHARACTERS")
        self.stdout.write("-" * 50)
        
        from allianceauth.eveonline.models import EveCharacter
        
        corps = Corporation.objects.filter(tracking_enabled=True)
        
        if not corps.exists():
            self.stdout.write(self.style.WARNING("⚠ No enabled corporations to check"))
            return
        
        for corp in corps:
            chars = EveCharacter.objects.filter(corporation_id=corp.corporation_id)
            
            if not chars.exists():
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ {corp.corporation_name}: No characters found"
                    )
                )
                self.stdout.write(
                    "  → Need a Director/CEO from this corporation to authenticate"
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ {corp.corporation_name}: Found {chars.count()} character(s)"
                    )
                )
                for char in chars:
                    self.stdout.write(f"  • {char.character_name}")
    
    def check_tokens(self):
        """Check for valid ESI tokens"""
        self.stdout.write("\n[3] ESI TOKENS")
        self.stdout.write("-" * 50)
        
        from allianceauth.eveonline.models import EveCharacter
        
        REQUIRED_SCOPES = app_settings.CORPINVENTORY_ESI_SCOPES
        
        self.stdout.write("Required scopes:")
        for scope in REQUIRED_SCOPES:
            self.stdout.write(f"  • {scope}")
        
        self.stdout.write()
        
        corps = Corporation.objects.filter(tracking_enabled=True)
        
        for corp in corps:
            chars = EveCharacter.objects.filter(corporation_id=corp.corporation_id)
            
            if not chars.exists():
                continue
            
            self.stdout.write(f"\n{corp.corporation_name}:")
            
            found_valid_token = False
            
            for char in chars:
                tokens = Token.objects.filter(character_id=char.character_id)
                
                if not tokens.exists():
                    self.stdout.write(
                        self.style.WARNING(f"  ⚠ {char.character_name}: No tokens")
                    )
                    continue
                
                for token in tokens:
                    token_scopes = token.get_scopes()
                    has_all_scopes = all(
                        scope in token_scopes for scope in REQUIRED_SCOPES
                    )
                    
                    is_valid = token.is_valid()
                    
                    if has_all_scopes and is_valid:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  ✓ {char.character_name}: Valid token with all scopes"
                            )
                        )
                        found_valid_token = True
                    else:
                        status_parts = []
                        
                        if not has_all_scopes:
                            missing = [
                                s for s in REQUIRED_SCOPES if s not in token_scopes
                            ]
                            status_parts.append(f"missing scopes: {missing}")
                        
                        if not is_valid:
                            status_parts.append("token expired/invalid")
                        
                        self.stdout.write(
                            self.style.ERROR(
                                f"  ✗ {char.character_name}: {', '.join(status_parts)}"
                            )
                        )
            
            if not found_valid_token:
                self.stdout.write(
                    self.style.ERROR(
                        f"  ✗ No valid tokens found for {corp.corporation_name}"
                    )
                )
                self.stdout.write(
                    "  → Character owner must add/refresh ESI token at /auth/eveauth"
                )
    
    def check_esi_connectivity(self):
        """Check if ESI can be reached"""
        self.stdout.write("\n[4] ESI CONNECTIVITY")
        self.stdout.write("-" * 50)
        
        try:
            from esi.clients import EsiClientProvider
            
            esi = EsiClientProvider()
            
            # Try a simple ESI call
            client = esi.client
            
            # Get server status (doesn't need authentication)
            status = client.Status.get_status().result()
            
            if status:
                self.stdout.write(
                    self.style.SUCCESS("✓ ESI is reachable")
                )
                return
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ Cannot reach ESI: {str(e)}")
            )
            self.stdout.write(
                "  → Check network connectivity and firewall"
            )
    
    def check_celery_beat(self):
        """Check Celery Beat configuration"""
        self.stdout.write("\n[5] CELERY BEAT CONFIGURATION")
        self.stdout.write("-" * 50)
        
        from django.conf import settings
        
        schedule = getattr(settings, 'CELERYBEAT_SCHEDULE', {})
        
        if 'corp_inventory_sync' not in schedule:
            self.stdout.write(
                self.style.ERROR(
                    "✗ corp_inventory_sync not in CELERYBEAT_SCHEDULE"
                )
            )
            self.stdout.write("  → Add this to your local.py settings:")
            self.stdout.write("""
    from celery.schedules import crontab
    
    CELERYBEAT_SCHEDULE['corp_inventory_sync'] = {
        'task': 'corp_inventory.tasks.sync_all_corporations',
        'schedule': crontab(minute='*/30'),  # Run every 30 minutes
    }
            """)
            return
        
        config = schedule['corp_inventory_sync']
        
        self.stdout.write(
            self.style.SUCCESS("✓ corp_inventory_sync configured")
        )
        self.stdout.write(f"  • Task: {config.get('task')}")
        self.stdout.write(f"  • Schedule: {config.get('schedule')}")
        
        # Check if crontab was imported
        try:
            from celery.schedules import crontab as crontab_check
            self.stdout.write(self.style.SUCCESS("✓ crontab imported"))
        except ImportError:
            self.stdout.write(
                self.style.ERROR(
                    "✗ crontab not imported in settings"
                )
            )
            self.stdout.write(
                "  → Add this import to your local.py: from celery.schedules import crontab"
            )
        
        # Check Celery Beat service status
        self.stdout.write("\nTo check if Celery Beat is running:")
        self.stdout.write("  Docker: docker-compose logs allianceauth_beat")
        self.stdout.write("  Systemd: systemctl status allianceauth-beat")
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(
            self.style.SUCCESS("\nDiagnostic complete!")
        )
        self.stdout.write("\nNext steps:")
        self.stdout.write("1. Ensure all ✓ checks pass")
        self.stdout.write("2. If ✗ issues exist, fix them")
        self.stdout.write("3. Restart Celery Beat: docker-compose restart allianceauth_beat")
        self.stdout.write("4. Check logs: docker-compose logs -f allianceauth_beat")
