from rest_framework import serializers

from api.serializers import ProductSerializer
from . import models


class PackageCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Package
        exclude = ('products',)


class PackageSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = models.Package
        fields = '__all__'

    def get_products(self, obj):
        return ProductSerializer(obj.products.all(), many=True).data
