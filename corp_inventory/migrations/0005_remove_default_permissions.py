"""
Data migration: remove auto-generated Django CRUD permissions for models that
should have default_permissions = ().

All non-Corporation models previously lacked default_permissions = (), so
Django auto-created add/change/delete/view permissions for each.  These
clutter the Alliance Auth permission picker and are never used by the app.
This migration removes them on existing installs.  Fresh installs are already
clean because the model Meta now declares default_permissions = ().
"""
from django.db import migrations


def remove_default_permissions(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    # Models that previously lacked default_permissions = ()
    model_names = [
        "hangardivision",
        "location",
        "hangaritem",
        "hangartransaction",
        "hangarsnapshot",
        "alertrule",
        "containerlog",
    ]
    prefixes = ("add_", "change_", "delete_", "view_")
    codenames = [f"{prefix}{model}" for model in model_names for prefix in prefixes]

    cts = ContentType.objects.filter(app_label="corp_inventory")
    deleted, _ = Permission.objects.filter(
        content_type__in=cts,
        codename__in=codenames,
    ).delete()
    if deleted:
        print(f"\n  Removed {deleted} unused auto-generated permissions.")


class Migration(migrations.Migration):

    dependencies = [
        ("corp_inventory", "0004_containerlog"),
    ]

    operations = [
        migrations.RunPython(
            remove_default_permissions,
            migrations.RunPython.noop,
        ),
    ]
