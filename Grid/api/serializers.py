from rest_framework import serializers
from .models import ApiLog

class ApiLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiLog
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'format': '%Y-%m-%d %H:%M:%S'},
        }