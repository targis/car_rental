from rest_framework import serializers

from .models import *


class CarSerializer(serializers.ModelSerializer):
    brand = serializers.StringRelatedField()
    features = serializers.StringRelatedField(many=True)

    class Meta:
        model = Car
        fields = '__all__'
        # fields = ['id', 'name', 'brand', 'features']


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = '__all__'


