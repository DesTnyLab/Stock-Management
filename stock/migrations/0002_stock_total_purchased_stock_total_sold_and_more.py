# Generated by Django 5.0.6 on 2024-11-27 17:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stock", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="stock",
            name="total_purchased",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="stock",
            name="total_sold",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="stock",
            name="product",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to="stock.product"
            ),
        ),
    ]