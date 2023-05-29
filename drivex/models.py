from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db.models import Q, Avg
from datetime import datetime
from django.urls import reverse
from django.utils import timezone
from .functions import UploadToPathAndRename

date_format = "%Y-%m-%d"


brands_upload_path = UploadToPathAndRename("brands")
cars_upload_path = UploadToPathAndRename("cars")


class Brand(models.Model):
    objects = models.Manager()

    name = models.CharField(max_length=32)
    logo = models.ImageField(upload_to="brands", null=True, blank=True)
    # cars

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class Feature(models.Model):
    objects = models.Manager()

    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class Car(models.Model):
    SEDAN = "SD"
    HATCHBACK = "HB"
    CROSSOVER = "CR"
    TRUCK = "TR"
    CONVERTIBLE = "CN"
    BODY_STYLES = [
        (SEDAN, "Sedan"),
        (HATCHBACK, "Hatchback"),
        (CROSSOVER, "SUV & Crossover"),
        (TRUCK, "Truck & Van"),
        (CONVERTIBLE, "Convertible"),
    ]
    GAS = "GS"
    DIESEL = "DS"
    ELECTRO = "EL"
    HYBRID = "HY"

    POWER_SOURCES = [
        (GAS, "Gasoline"),
        (DIESEL, "Diesel"),
        (ELECTRO, "Electricity"),
        (HYBRID, "Hybrid"),
    ]

    AUTOMATIC = "AT"
    MANUAL = "MT"
    TRANSMISSIONS = [
        (AUTOMATIC, "Automatic"),
        (MANUAL, "Manual"),
    ]

    objects = models.Manager()
    name = models.CharField(max_length=32)
    brand = models.ForeignKey(Brand, related_name="cars", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="cars", default="cars/car.png", blank=True)
    category = models.ForeignKey(
        Category, related_name="cars", on_delete=models.SET_NULL, null=True, blank=True
    )

    style = models.CharField(max_length=2, choices=BODY_STYLES, default=SEDAN)
    power = models.CharField(max_length=2, choices=POWER_SOURCES, default=GAS)
    transmission = models.CharField(max_length=2, choices=TRANSMISSIONS, default=MANUAL)
    capacity = models.FloatField(default=1.6)  # engine capacity
    passengers = models.PositiveSmallIntegerField(default=5)
    doors = models.PositiveSmallIntegerField(default=4)
    boot_space = models.PositiveIntegerField(default=500)
    consumption = models.FloatField(default=8.0)  # litres per 100 km
    features = models.ManyToManyField(Feature, related_name="cars", blank=True)
    rating = models.FloatField(null=True, blank=True)
    badge = models.ForeignKey(
        "Badge", related_name="cars", on_delete=models.SET_NULL, null=True, blank=True
    )
    price = models.PositiveIntegerField(default=20)
    favorites = models.ManyToManyField(User, blank=True, related_name="favorites")

    def __str__(self):
        return f"{self.brand.name} {self.name}"

    def url(self):
        return reverse("drivex:car-detail", kwargs={"pk": self.id})

    def is_available(self, from_date, to_date):
        # Check if the car is available for the selected dates
        wanted_start = datetime.strptime(from_date, date_format).date()
        wanted_end = datetime.strptime(to_date, date_format).date()
        reservations = Order.objects.filter(
            car=self, status__in=[Order.ACTIVE, Order.NEW]
        )
        for reservation in reservations:
            if (reservation.date_start <= wanted_start <= reservation.date_end) or (
                wanted_end < wanted_start
            ):
                return False
            if reservation.date_start <= wanted_end <= reservation.date_end:
                return False
            if (
                wanted_start <= reservation.date_start
                and wanted_end >= reservation.date_end
            ):
                return False
        return True


class Badge(models.Model):
    VIOLET = "#7400C8"
    ORANGE = "#ff8e30"
    GREEN = "#70d628"
    BLUE = "#12bbee"
    RED = "#EA0D01"
    COLORS = [
        (VIOLET, "violet"),
        (ORANGE, "orange"),
        (GREEN, "green"),
        (BLUE, "blue"),
        (RED, "red"),
    ]

    objects = models.Manager()

    name = models.CharField(max_length=32)
    color = models.CharField(max_length=7, choices=COLORS, default=VIOLET)
    # cars

    def __str__(self):
        return self.name


class Profile(models.Model):
    objects = models.Manager()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(
        upload_to="users", default="users/user.jpg", max_length=128, blank=True
    )
    name = models.CharField(max_length=32, blank=True)
    tel = models.CharField(max_length=10, blank=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        try:
            instance.profile.save()
        except Profile.DoesNotExist:
            Profile.objects.create(user=instance)


class Order(models.Model):
    NEW = "NW"
    ACTIVE = "AC"
    CLOSED = "CL"

    STATUSES = [
        (NEW, "New"),
        (ACTIVE, "Active"),
        (CLOSED, "Closed"),
    ]

    objects = models.Manager()

    user = models.ForeignKey(User, related_name="orders", on_delete=models.CASCADE)
    car = models.ForeignKey(Car, related_name="orders", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now=True)
    date_start = models.DateField(default=timezone.now)
    date_end = models.DateField()
    status = models.CharField(max_length=2, choices=STATUSES, default=NEW)
    number = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"self.number"


@receiver(pre_save, sender=Order)
def add_order_number(sender, instance, *args, **kwargs):
    if not instance.number:
        date_part = timezone.now().strftime("%Y%m%d")
        last_order = (
            Order.objects.filter(number__startswith=date_part).order_by("number").last()
        )
        if not last_order:
            new_order_number = date_part + "-0001"
        else:
            last_order_number = last_order.number
            new_order_number = int(last_order_number.split("-")[-1]) + 1
            new_order_number = date_part + f"-{new_order_number:04}"
        instance.number = new_order_number


class Review(models.Model):
    objects = models.Manager()
    user = models.ForeignKey(User, related_name="reviews", on_delete=models.CASCADE)
    car = models.ForeignKey(Car, related_name="reviews", on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True)
    rate = models.PositiveSmallIntegerField(null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.text

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        rating = self.car.reviews.aggregate(Avg("rate"))["rate__avg"]
        self.car.rating = rating
        self.car.save()

    class Meta:
        ordering = ["-created"]
