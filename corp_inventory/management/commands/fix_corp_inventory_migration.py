"""
Management command to fix migration issues in Corp Inventory
Resolves the migration history conflict from earlier versions
"""

import logging
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import connection

logger = logging.getLogger(__name__)


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

        # Check if we have the migration issue
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    "SELECT name FROM django_migrations "
                    "WHERE app = 'corp_inventory' AND name LIKE '0002%rename%'"
                )
                result = cursor.fetchone()
                
                if not result:
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
