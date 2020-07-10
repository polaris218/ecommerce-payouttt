from rest_framework import serializers
from . import models


class PackageCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Package
        exclude = ('products',)


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Package
        fileds = '__all__'
