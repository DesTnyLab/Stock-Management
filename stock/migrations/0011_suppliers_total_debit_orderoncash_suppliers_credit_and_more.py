# Generated by Django 5.1.3 on 2024-12-14 06:55

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stock", "0010_remove_product_sh_code_product_hs_code_order_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="suppliers",
            name="total_debit",
            field=models.FloatField(default=0.0),
        ),
        migrations.CreateModel(
            name="OrderOnCash",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.FloatField(default=0.0)),
                ("date", models.DateField(default=django.utils.timezone.now)),
                (
                    "particulars",
                    models.CharField(default=" ", editable=False, max_length=255),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="stock.order"
                    ),
                ),
                (
                    "suppliers",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="stock.suppliers",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Suppliers_credit",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.FloatField(default=0.0)),
                ("date", models.DateField(default=django.utils.timezone.now)),
                (
                    "particulars",
                    models.CharField(default=" ", editable=False, max_length=255),
                ),
                (
                    "order",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="stock.order"
                    ),
                ),
                (
                    "suppliers",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="stock.suppliers",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Suppliers_debit",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.FloatField(default=0.0)),
                ("date", models.DateField(default=django.utils.timezone.now)),
                (
                    "particulars",
                    models.CharField(default="Cheque", editable=False, max_length=255),
                ),
                (
                    "suppliers",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="stock.suppliers",
                    ),
                ),
            ],
        ),
    ]
