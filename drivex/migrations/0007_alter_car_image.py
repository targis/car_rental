# Generated by Django 4.1.7 on 2023-05-17 09:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("drivex", "0006_alter_brand_logo_alter_car_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="car",
            name="image",
            field=models.ImageField(
                blank=True, default="cars/car.png", upload_to="cars"
            ),
        ),
    ]