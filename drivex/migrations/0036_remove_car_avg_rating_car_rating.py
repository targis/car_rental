# Generated by Django 4.1.7 on 2023-05-28 11:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("drivex", "0035_remove_car_rating_alter_car_avg_rating_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="car",
            name="avg_rating",
        ),
        migrations.AddField(
            model_name="car",
            name="rating",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
