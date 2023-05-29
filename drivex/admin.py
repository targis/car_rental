from django.contrib import admin
from .models import *


def bulk_update(queryset, update_fields):
    pass


class CarInline(admin.TabularInline):
    model = Car
    max_num = 20
    fields = ['name', 'category', 'price', 'features']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = [CarInline]


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'style']


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Order._meta.get_fields()]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'text', 'rate', 'car']
