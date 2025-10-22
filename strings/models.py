from django.db import models
import hashlib
import json

class StringAnalysis(models.Model):
    id = models.CharField(primary_key=True, max_length=64)  # SHA256 hash
    value = models.TextField(unique=True)
    length = models.IntegerField()
    is_palindrome = models.BooleanField()
    unique_characters = models.IntegerField()
    word_count = models.IntegerField()
    character_frequency_map = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'string_analysis'
        ordering = ['-created_at']

    @classmethod
    def analyze_string(cls, string_value):
        """Analyze string and compute all properties"""
        # Compute SHA256 hash as ID
        hash_id = hashlib.sha256(string_value.encode('utf-8')).hexdigest()
        
        # Convert to lowercase for case-insensitive analysis
        lower_string = string_value.lower()
        
        # Compute properties
        length = len(string_value)
        is_palindrome = lower_string == lower_string[::-1]
        unique_chars = len(set(lower_string))
        word_count = len(string_value.split())
        
        # Character frequency (case-insensitive)
        freq_map = {}
        for char in lower_string:
            freq_map[char] = freq_map.get(char, 0) + 1
        
        return cls(
            id=hash_id,
            value=string_value,
            length=length,
            is_palindrome=is_palindrome,
            unique_characters=unique_chars,
            word_count=word_count,
            character_frequency_map=freq_map
        )