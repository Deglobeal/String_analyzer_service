from django.db import models
import hashlib
import json

class StringAnalysis(models.Model):
    id = models.CharField(max_length=64, primary_key=True)  # SHA256 hash
    value = models.TextField(unique=True)
    length = models.IntegerField()
    is_palindrome = models.BooleanField()
    unique_characters = models.IntegerField()
    word_count = models.IntegerField()
    sha256_hash = models.CharField(max_length=64)
    character_frequency_map = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'string_analysis'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.value} (ID: {self.id})"