# Generated by Django 4.1.7 on 2023-05-25 15:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("drivex", "0027_carrating"),
    ]

    operations = [
        migrations.AddField(
            model_name="car",
            name="avg_rating",
            field=models.FloatField(blank=True, default=5.0, null=True),
        ),
    ]
