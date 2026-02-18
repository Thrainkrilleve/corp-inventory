"""
Management command to fix migration issues in Corp Inventory
Resolves the migration history conflict from earlier versions
"""

import logging
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import connection

logger = logging.getLogger(__name__)

MIGRATION_0003_RENAME = (
    "0003_rename_corp_inv_corp_active_idx_"
    "corp_invent_corpora_da626d_idx_and_more"
)


class Command(BaseCommand):
    help = (
        'Fix migration issues for Corp Inventory. '
        'This command resolves migration history conflicts from earlier versions.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force fix without confirmation',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                'Corp Inventory Migration Fix'
            )
        )
        self.stdout.write('-' * 50)

        def _table_exists(cursor, table_name):
            cursor.execute("SHOW TABLES LIKE %s", [table_name])
            return cursor.fetchone() is not None

        def _index_exists(cursor, table_name, index_name):
            cursor.execute(
                f"SHOW INDEX FROM `{table_name}` WHERE Key_name = %s",
                [index_name],
            )
            return cursor.fetchone() is not None

        # Check if we have the migration issue
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    "SELECT name FROM django_migrations "
                    "WHERE app = 'corp_inventory' AND name LIKE '0002%rename%'"
                )
                result = cursor.fetchone()

                cursor.execute(
                    "SELECT name FROM django_migrations "
                    "WHERE app = 'corp_inventory' AND name LIKE '0003%rename%'"
                )
                has_0003 = cursor.fetchone() is not None
                
                if not result:
                    # No legacy 0002 rename. Check for 0003 rename failure case.
                    if not has_0003:
                        if _table_exists(cursor, "corp_inventory_hangaritem"):
                            legacy_index = "corp_inv_corp_active_idx"
                            legacy_index_missing = not _index_exists(
                                cursor,
                                "corp_inventory_hangaritem",
                                legacy_index,
                            )
                            if legacy_index_missing:
                                self.stdout.write(
                                    self.style.WARNING(
                                        "⚠ 0003 rename migration pending and legacy index is missing."
                                    )
                                )
                                if not options['force']:
                                    confirm = input(
                                        'Fake-apply 0003 rename migration now? (y/n): '
                                    ).strip().lower()
                                    if confirm != 'y':
                                        self.stdout.write('Cancelled.')
                                        return

                                self.stdout.write('Applying 0003 fix...')
                                call_command(
                                    'migrate',
                                    'corp_inventory',
                                    MIGRATION_0003_RENAME,
                                    '--fake',
                                    verbosity=0,
                                )
                                self.stdout.write(
                                    self.style.SUCCESS('✓ 0003 migration marked as applied.')
                                )
                                self.stdout.write('Running migrations...')
                                call_command(
                                    'migrate',
                                    'corp_inventory',
                                    verbosity=1,
                                )
                                self.stdout.write('')
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        '✓ Corp Inventory migration issues fixed!'
                                    )
                                )
                                return

                    self.stdout.write(
                        self.style.SUCCESS(
                            '✓ No migration issues detected. '
                            'Corp Inventory is ready to use.'
                        )
                    )
                    return

                self.stdout.write(
                    self.style.WARNING(
                        '⚠ Found legacy migration in database: ' + result[0]
                    )
                )
                self.stdout.write(
                    'This is causing the index rename errors on migration.'
                )
                self.stdout.write('')

                if not options['force']:
                    confirm = input(
                        'Fix this issue now? (y/n): '
                    ).strip().lower()
                    if confirm != 'y':
                        self.stdout.write('Cancelled.')
                        return

                # Apply the fix
                self.stdout.write('Applying fix...')
                call_command(
                    'migrate',
                    'corp_inventory',
                    '0001_initial',
                    '--fake',
                    verbosity=0,
                )

                self.stdout.write(
                    self.style.SUCCESS('✓ Migration history reset.')
                )
                self.stdout.write('Running migrations...')
                
                call_command(
                    'migrate',
                    'corp_inventory',
                    verbosity=1,
                )

                self.stdout.write('')
                self.stdout.write(
                    self.style.SUCCESS(
                        '✓ Corp Inventory migration issues fixed!'
                    )
                )
                self.stdout.write('Your database is now up to date.')

            except Exception as e:
                raise CommandError(f'Error fixing migrations: {str(e)}')
