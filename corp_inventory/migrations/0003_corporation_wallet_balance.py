from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("corp_inventory", "0002_empty"),
    ]

    operations = [
        migrations.AddField(
            model_name="corporation",
            name="wallet_balance",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="Corporation master wallet balance in ISK",
                max_digits=20,
                null=True,
            ),
        ),
    ]
