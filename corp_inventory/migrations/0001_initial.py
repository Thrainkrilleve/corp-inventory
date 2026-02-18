# Generated migration for Corp Inventory

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Corporation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('corporation_id', models.IntegerField(db_index=True, unique=True)),
                ('corporation_name', models.CharField(max_length=254)),
                ('tracking_enabled', models.BooleanField(default=True)),
                ('last_sync', models.DateTimeField(blank=True, null=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Corporation',
                'verbose_name_plural': 'Corporations',
                'default_permissions': (),
                'permissions': (
                    ('basic_access', 'Can access Corp Inventory'),
                    ('view_hangar', 'Can view corporation hangars'),
                    ('view_transactions', 'Can view hangar transactions'),
                    ('manage_tracking', 'Can manage hangar tracking'),
                    ('manage_corporations', 'Can add/remove tracked corporations'),
                ),
            },
        ),
        migrations.CreateModel(
            name='HangarDivision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('division_id', models.IntegerField()),
                ('division_name', models.CharField(max_length=100)),
                ('corporation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='divisions', to='corp_inventory.corporation')),
            ],
            options={
                'verbose_name': 'Hangar Division',
                'verbose_name_plural': 'Hangar Divisions',
                'ordering': ['corporation', 'division_id'],
                'unique_together': {('corporation', 'division_id')},
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location_id', models.BigIntegerField(db_index=True, unique=True)),
                ('location_name', models.CharField(max_length=254)),
                ('location_type', models.CharField(max_length=50)),
                ('solar_system_id', models.IntegerField(blank=True, null=True)),
                ('solar_system_name', models.CharField(blank=True, max_length=100)),
                ('region_id', models.IntegerField(blank=True, null=True)),
                ('region_name', models.CharField(blank=True, max_length=100)),
                ('last_update', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Location',
                'verbose_name_plural': 'Locations',
                'ordering': ['location_name'],
            },
        ),
        migrations.CreateModel(
            name='HangarItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_id', models.BigIntegerField(db_index=True, unique=True)),
                ('type_id', models.IntegerField(db_index=True)),
                ('type_name', models.CharField(max_length=254)),
                ('quantity', models.BigIntegerField(default=1)),
                ('estimated_value', models.DecimalField(decimal_places=2, default=0, max_digits=20, help_text='Estimated ISK value')),
                ('is_singleton', models.BooleanField(default=False)),
                ('is_blueprint_copy', models.BooleanField(default=False)),
                ('first_seen', models.DateTimeField(auto_now_add=True)),
                ('last_seen', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('corporation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hangar_items', to='corp_inventory.corporation')),
                ('division', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='items', to='corp_inventory.hangardivision')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='corp_inventory.location')),
            ],
            options={
                'verbose_name': 'Hangar Item',
                'verbose_name_plural': 'Hangar Items',
                'ordering': ['-last_seen'],
            },
        ),
        migrations.CreateModel(
            name='HangarTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(
                    choices=[('ADD', 'Addition'), ('REMOVE', 'Removal'), ('MOVE', 'Movement'), ('CHANGE', 'Quantity Change')],
                    db_index=True,
                    max_length=10
                )),
                ('type_id', models.IntegerField(db_index=True)),
                ('type_name', models.CharField(max_length=254)),
                ('quantity_change', models.BigIntegerField()),
                ('old_quantity', models.BigIntegerField(default=0)),
                ('new_quantity', models.BigIntegerField(default=0)),
                ('estimated_value', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('character_id', models.IntegerField(blank=True, db_index=True, null=True)),
                ('character_name', models.CharField(blank=True, max_length=254)),
                ('detected_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('notification_sent', models.BooleanField(default=False)),
                ('corporation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='corp_inventory.corporation')),
                ('division', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='corp_inventory.hangardivision')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='corp_inventory.location')),
            ],
            options={
                'verbose_name': 'Hangar Transaction',
                'verbose_name_plural': 'Hangar Transactions',
                'ordering': ['-detected_at'],
            },
        ),
        migrations.CreateModel(
            name='HangarSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('snapshot_time', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('total_items', models.IntegerField(default=0)),
                ('total_value', models.DecimalField(decimal_places=2, default=0, max_digits=20)),
                ('snapshot_data', models.JSONField(default=dict)),
                ('corporation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='snapshots', to='corp_inventory.corporation')),
            ],
            options={
                'verbose_name': 'Hangar Snapshot',
                'verbose_name_plural': 'Hangar Snapshots',
                'ordering': ['-snapshot_time'],
            },
        ),
        migrations.CreateModel(
            name='AlertRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('alert_type', models.CharField(
                    choices=[('ITEM_ADDED', 'Item Added'), ('ITEM_REMOVED', 'Item Removed'), ('VALUE_THRESHOLD', 'Value Threshold Exceeded'), ('QUANTITY_CHANGE', 'Quantity Changed')],
                    max_length=20
                )),
                ('type_id', models.IntegerField(blank=True, null=True)),
                ('type_name', models.CharField(blank=True, default='', max_length=254, null=True)),
                ('value_threshold', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('quantity_threshold', models.BigIntegerField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('corporation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alert_rules', to='corp_inventory.corporation')),
                ('division', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='corp_inventory.hangardivision')),
                ('notify_users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Alert Rule',
                'verbose_name_plural': 'Alert Rules',
                'ordering': ['corporation', 'name'],
            },
        ),
        migrations.AddIndex(
            model_name='hangaritem',
            index=models.Index(fields=['corporation', 'is_active']),
        ),
        migrations.AddIndex(
            model_name='hangaritem',
            index=models.Index(fields=['type_id', 'is_active']),
        ),
        migrations.AddIndex(
            model_name='hangartransaction',
            index=models.Index(fields=['corporation', '-detected_at']),
        ),
        migrations.AddIndex(
            model_name='hangartransaction',
            index=models.Index(fields=['type_id', '-detected_at']),
        ),
        migrations.AddIndex(
            model_name='hangartransaction',
            index=models.Index(fields=['character_id', '-detected_at']),
        ),
        migrations.AddIndex(
            model_name='hangarsnapshot',
            index=models.Index(fields=['corporation', '-snapshot_time']),
        ),
    ]
