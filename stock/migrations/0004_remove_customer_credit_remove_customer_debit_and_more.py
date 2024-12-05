# Generated by Django 5.0.6 on 2024-12-05 04:13

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stock", "0003_remove_billitem_products_remove_billitem_quantity_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="customer",
            name="credit",
        ),
        migrations.RemoveField(
            model_name="customer",
            name="debit",
        ),
        migrations.AddField(
            model_name="billitem",
            name="total",
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name="product",
            name="product_code",
            field=models.CharField(default=" ", max_length=50),
        ),
        migrations.AlterField(
            model_name="bill",
            name="bill_no",
            field=models.PositiveIntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name="bill",
            name="customer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="stock.customer"
            ),
        ),
        migrations.AlterField(
            model_name="billitem",
            name="bill",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="stock.bill"
            ),
        ),
        migrations.AlterField(
            model_name="customer",
            name="company",
            field=models.CharField(default=" ", max_length=50),
        ),
        migrations.CreateModel(
            name="Credit",
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
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="stock.customer"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Debit",
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
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="stock.customer"
                    ),
                ),
            ],
        ),
    ]
