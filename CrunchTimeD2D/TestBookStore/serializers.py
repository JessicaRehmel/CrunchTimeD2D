from rest_framework import serializers
from .models import OnixFile


class OnixSerializer(serializers.Serializer):
    data = serializers.CharField(style={'base_template': 'textarea.html'})

    def create(self, validated_data):
        return OnixFile.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.data = validated_data.get('data', instance.data)
        instance.save()
        return instance