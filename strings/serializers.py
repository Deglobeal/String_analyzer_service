from rest_framework import serializers
from .models import StringAnalysis

class StringPropertiesSerializer(serializers.Serializer):
    length = serializers.IntegerField()
    is_palindrome = serializers.BooleanField()
    unique_characters = serializers.IntegerField()
    word_count = serializers.IntegerField()
    sha256_hash = serializers.CharField(source='id')
    character_frequency_map = serializers.JSONField()

class StringAnalysisSerializer(serializers.ModelSerializer):
    properties = StringPropertiesSerializer(source='*')
    
    class Meta:
        model = StringAnalysis
        fields = ['id', 'value', 'properties', 'created_at']

class StringCreateSerializer(serializers.Serializer):
    value = serializers.CharField(required=True, max_length=10000)
    
    def validate_value(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("Value must be a string")
        return value