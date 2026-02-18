# Automated schema migration to match new model definitions
# Handles field renames, type changes, and new fields without interactive prompts

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('corp_inventory', '0001_initial'),
    ]

    operations = [
        # Rename Corporation fields
        migrations.RenameField(
            model_name='corporation',
            old_name='updated_at',
            new_name='last_update',
        ),
        migrations.RenameField(
            model_name='corporation',
            old_name='is_active',
            new_name='tracking_enabled',
        ),
        
        # Remove old Corporation fields
        migrations.RemoveField(
            model_name='corporation',
            name='ticker',
        ),
        
        # Alter Corporation field types if needed
        migrations.AlterField(
            model_name='corporation',
            name='corporation_id',
            field=models.IntegerField(db_index=True, unique=True),
        ),
        migrations.AlterField(
            model_name='corporation',
            name='corporation_name',
            field=models.CharField(max_length=254),
        ),
        
        # Rename HangarItem fields
        migrations.RenameField(
            model_name='hangaritem',
            old_name='created_at',
            new_name='first_seen',
        ),
        
        # Remove old HangarItem fields
        migrations.RemoveField(
            model_name='hangaritem',
            name='estimated_price',
        ),
        migrations.RemoveField(
            model_name='hangaritem',
            name='location_flag',
        ),
        
        # Add new HangarItem fields
        migrations.AddField(
            model_name='hangaritem',
            name='estimated_value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20, help_text='Estimated ISK value'),
        ),
        migrations.AddField(
            model_name='hangaritem',
            name='is_active',
            field=models.BooleanField(db_index=True, default=True),
        ),
        
        # Alter HangarItem field types
        migrations.AlterField(
            model_name='hangaritem',
            name='quantity',
            field=models.BigIntegerField(default=1),
        ),
        
        # Rename Location fields
        migrations.RenameField(
            model_name='location',
            old_name='updated_at',
            new_name='last_update',
        ),
        
        # Remove old Location fields
        migrations.RemoveField(
            model_name='location',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='location',
            name='system_id',
        ),
        migrations.RemoveField(
            model_name='location',
            name='system_name',
        ),
        
        # Add new Location fields
        migrations.AddField(
            model_name='location',
            name='solar_system_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='location',
            name='solar_system_name',
            field=models.CharField(max_length=100, blank=True, default=''),
        ),
        
        # Alter Location field types
        migrations.AlterField(
            model_name='location',
            name='location_name',
            field=models.CharField(max_length=254),
        ),
        migrations.AlterField(
            model_name='location',
            name='region_name',
            field=models.CharField(max_length=100, blank=True, default=''),
        ),
        
        # HangarTransaction updates
        migrations.AddField(
            model_name='hangartransaction',
            name='character_id',
            field=models.IntegerField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='hangartransaction',
            name='character_name',
            field=models.CharField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='hangartransaction',
            name='notification_sent',
            field=models.BooleanField(default=False),
        ),
        
        # Alter HangarTransaction field types
        migrations.AlterField(
            model_name='hangartransaction',
            name='transaction_type',
            field=models.CharField(choices=[('ADD', 'Addition'), ('REMOVE', 'Removal'), ('MOVE', 'Movement'), ('CHANGE', 'Quantity Change')], db_index=True, max_length=10),
        ),
        
        # HangarSnapshot updates
        migrations.RemoveField(
            model_name='hangarsnapshot',
            name='snapshot_date',
        ),
        migrations.RemoveField(
            model_name='hangarsnapshot',
            name='unique_types',
        ),
        
        migrations.AddField(
            model_name='hangarsnapshot',
            name='snapshot_time',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='hangarsnapshot',
            name='snapshot_data',
            field=models.JSONField(default=dict),
        ),
        
        # AlertRule updates
        migrations.RenameField(
            model_name='alertrule',
            old_name='threshold_value',
            new_name='quantity_threshold',
        ),
        
        migrations.RemoveField(
            model_name='alertrule',
            name='updated_at',
        ),
        
        migrations.AddField(
            model_name='alertrule',
            name='value_threshold',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='alertrule',
            name='notify_users',
            field=models.ManyToManyField(blank=True, to='auth.user'),
        ),
        
        # Alter AlertRule field types
        migrations.AlterField(
            model_name='alertrule',
            name='type_name',
            field=models.CharField(blank=True, default='', max_length=254),
        ),
        
        # Remove old indexes (use RemoveIndex operations)
        migrations.RemoveIndex(
            model_name='hangaritem',
            name='corp_invent_corp_loc_idx',
        ),
        migrations.RemoveIndex(
            model_name='hangaritem',
            name='corp_invent_type_id_idx',
        ),
        migrations.RemoveIndex(
            model_name='hangartransaction',
            name='corp_invent_detecte_idx',
        ),
        migrations.RemoveIndex(
            model_name='hangartransaction',
            name='corp_invent_corp_type_idx',
        ),
        
        # Add new indexes
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
