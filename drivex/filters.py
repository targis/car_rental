import django_filters
from django import forms
import django_filters

from .models import *


class CarFilter(django_filters.FilterSet):
    brand = django_filters.ModelChoiceFilter(queryset=Brand.objects.all())
    name = django_filters.CharFilter(field_name='name', lookup_expr="icontains")
    price__gt = django_filters.NumberFilter(field_name='price', lookup_expr='gt')
    price__lt = django_filters.NumberFilter(field_name='price', lookup_expr='lt')
    transmission = django_filters.ChoiceFilter(
        field_name='transmission', choices=Car.TRANSMISSIONS, widget=forms.RadioSelect()
    )
    fuel_type = django_filters.ChoiceFilter(
        field_name='power', label='Fuel Type', choices=Car.POWER_SOURCES, widget=forms.RadioSelect()
    )

    order_by = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('price', 'price'),
        ),
        exclude=True
    )

    class Meta:
        model = Car
        fields = ['name', 'brand', 'price__lt', 'price__gt', 'transmission', 'fuel_type', 'order_by']
        exclude = ['order_by']
