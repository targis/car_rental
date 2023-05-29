# Generated by Django 4.1.7 on 2023-05-15 16:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("drivex", "0002_rename_model_car_name_brand_logo_car_image_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="car",
            name="features",
            field=models.ManyToManyField(
                blank=True, null=True, related_name="cars", to="drivex.feature"
            ),
        ),
    ]