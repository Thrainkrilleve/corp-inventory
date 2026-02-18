from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("corp_inventory", "0003_corporation_wallet_balance"),
    ]

    operations = [
        migrations.CreateModel(
            name="ContainerLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("character_id", models.IntegerField(db_index=True)),
                ("character_name", models.CharField(blank=True, default="", max_length=254)),
                ("action", models.CharField(
                    choices=[
                        ("add", "Added"), ("assemble", "Assembled"),
                        ("configure", "Configured"), ("enter_password", "Entered Password"),
                        ("lock", "Locked"), ("move", "Moved"),
                        ("repackage", "Repackaged"), ("set_name", "Set Name"),
                        ("set_password", "Set Password"), ("take", "Took"),
                        ("unlock", "Unlocked"),
                    ],
                    db_index=True, max_length=30,
                )),
                ("type_id", models.IntegerField(blank=True, db_index=True, null=True)),
                ("type_name", models.CharField(blank=True, default="", max_length=254)),
                ("quantity", models.IntegerField(blank=True, null=True)),
                ("container_id", models.BigIntegerField(db_index=True)),
                ("container_type_id", models.IntegerField(blank=True, null=True)),
                ("container_type_name", models.CharField(blank=True, default="", max_length=254)),
                ("location_id", models.BigIntegerField(blank=True, null=True)),
                ("location_flag", models.CharField(blank=True, default="", max_length=100)),
                ("logged_at", models.DateTimeField(db_index=True)),
                ("corporation", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="container_logs",
                    to="corp_inventory.corporation",
                )),
            ],
            options={
                "verbose_name": "Container Log",
                "verbose_name_plural": "Container Logs",
                "ordering": ["-logged_at"],
                "unique_together": {
                    ("corporation", "character_id", "container_id", "action", "type_id", "quantity", "logged_at")
                },
                "indexes": [
                    models.Index(
                        fields=["corporation", "-logged_at"],
                        name="corp_inv_clog_corp_idx",
                    ),
                    models.Index(
                        fields=["character_id", "-logged_at"],
                        name="corp_inv_clog_char_idx",
                    ),
                ],
            },
        ),
    ]
