import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class CorpInventoryConfig(AppConfig):
    name = "corp_inventory"
    label = "corp_inventory"
    verbose_name = "Corp Inventory"
    default = True
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        """Register signal handlers, admin, hooks, and Celery beat schedule."""
        import corp_inventory.signals  # noqa: F401
        import corp_inventory.admin  # noqa: F401
        import corp_inventory.auth_hooks  # noqa: F401

        self._register_beat_schedule()

    @staticmethod
    def _register_beat_schedule():
        """
        Auto-create the periodic Celery Beat task for sync_all_corporations
        if django-celery-beat is installed and the DB is ready.
        The interval is controlled by CORPINVENTORY_SYNC_INTERVAL (default 30 min).
        """
        try:
            from django_celery_beat.models import PeriodicTask, IntervalSchedule
            from . import app_settings

            interval_minutes = app_settings.CORPINVENTORY_SYNC_INTERVAL

            schedule, _ = IntervalSchedule.objects.get_or_create(
                every=interval_minutes,
                period=IntervalSchedule.MINUTES,
            )

            PeriodicTask.objects.update_or_create(
                name="Corp Inventory: Sync All Corporations",
                defaults={
                    "task": "corp_inventory.tasks.sync_all_corporations",
                    "interval": schedule,
                    "enabled": True,
                },
            )
            logger.debug(
                f"Corp Inventory beat schedule registered: every {interval_minutes} minutes"
            )
        except Exception:
            # DB may not be ready yet (e.g. during migrations / test setup) — skip silently.
            pass
