# Generated by Django 4.1.7 on 2023-05-25 09:05

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("drivex", "0024_alter_car_consumption"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="date_start",
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
