# Empty migration to resolve migration history conflict
# This migration exists only to satisfy the migration history recorded in the database
# from earlier versions and contains no operations

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corp_inventory', '0001_initial'),
    ]

    operations = [
    ]
