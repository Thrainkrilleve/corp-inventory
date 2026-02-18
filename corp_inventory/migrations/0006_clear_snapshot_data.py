"""
Data migration: clear snapshot_data JSON blobs from all existing HangarSnapshot rows.

The snapshot_data field stored a full copy of all item data as JSON on every
sync run (every 30 min). For a corp with 5,000 items this is ~500KB per row
and grows indefinitely. This migration zeroes those out, freeing the space.

Going forward, tasks.py writes snapshot_data={} explicitly, so new rows are clean.
"""
from django.db import migrations


def clear_snapshot_data(apps, schema_editor):
    HangarSnapshot = apps.get_model("corp_inventory", "HangarSnapshot")
    updated = HangarSnapshot.objects.exclude(snapshot_data={}).update(snapshot_data={})
    if updated:
        print(f"\n  Cleared snapshot_data JSON from {updated} HangarSnapshot row(s).")


class Migration(migrations.Migration):

    dependencies = [
        ("corp_inventory", "0005_remove_default_permissions"),
    ]

    operations = [
        migrations.RunPython(
            clear_snapshot_data,
            migrations.RunPython.noop,
        ),
    ]
