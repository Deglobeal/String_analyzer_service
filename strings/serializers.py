from rest_framework import serializers
from .models import StringAnalysis

class StringAnalysisSerializer(serializers.ModelSerializer):
    properties = serializers.SerializerMethodField()
    
    class Meta:
        model = StringAnalysis
        fields = ['id', 'value', 'properties', 'created_at']
    
    def get_properties(self, obj):
        return {
            'length': obj.length,
            'is_palindrome': obj.is_palindrome,
            'unique_characters': obj.unique_characters,
            'word_count': obj.word_count,
            'sha256_hash': obj.id,
            'character_frequency_map': obj.character_frequency_map
        }

class StringInputSerializer(serializers.Serializer):
    value = serializers.CharField(required=True, max_length=10000)
    
    def validate_value(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("Value must be a string")
        if not value.strip():
            raise serializers.ValidationError("Value cannot be empty")
        return value