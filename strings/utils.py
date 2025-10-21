import hashlib
import re
from collections import Counter
from typing import Dict, Any

class StringAnalyzer:
    @staticmethod
    def analyze_string(value: str) -> Dict[str, Any]:
        """Analyze a string and return all computed properties."""
        
        # Basic properties
        length = len(value)
        
        # Palindrome check (case-insensitive, ignore non-alphanumeric)
        cleaned_string = re.sub(r'[^a-zA-Z0-9]', '', value.lower())
        is_palindrome = cleaned_string == cleaned_string[::-1] if cleaned_string else True
        
        # Unique characters count
        unique_characters = len(set(value))
        
        # Word count (split by whitespace)
        word_count = len(value.split())
        
        # SHA-256 hash
        sha256_hash = hashlib.sha256(value.encode('utf-8')).hexdigest()
        
        # Character frequency map
        character_frequency_map = dict(Counter(value))
        
        return {
            'id': sha256_hash,
            'value': value,
            'properties': {
                'length': length,
                'is_palindrome': is_palindrome,
                'unique_characters': unique_characters,
                'word_count': word_count,
                'sha256_hash': sha256_hash,
                'character_frequency_map': character_frequency_map
            },
            'created_at': None  # Will be set by serializer
        }

class NaturalLanguageParser:
    @staticmethod
    def parse_query(query: str) -> Dict[str, Any]:
        """Parse natural language query into filter parameters."""
        query = query.lower().strip()
        parsed_filters = {}
        
        # Map of keywords to filters
        keyword_mappings = {
            'palindrome': {'is_palindrome': True},
            'palindromic': {'is_palindrome': True},
            'single word': {'word_count': 1},
            'one word': {'word_count': 1},
            'two words': {'word_count': 2},
            'three words': {'word_count': 3},
            'contains z': {'contains_character': 'z'},
            'containing z': {'contains_character': 'z'},
            'has z': {'contains_character': 'z'},
            'with z': {'contains_character': 'z'},
            'contains a': {'contains_character': 'a'},
            'containing a': {'contains_character': 'a'},
            'has a': {'contains_character': 'a'},
            'with a': {'contains_character': 'a'},
            'first vowel': {'contains_character': 'a'},
        }
        
        # Length-based patterns
        length_patterns = [
            (r'longer than (\d+) characters', 'min_length'),
            (r'length greater than (\d+)', 'min_length'),
            (r'more than (\d+) characters', 'min_length'),
            (r'shorter than (\d+) characters', 'max_length'),
            (r'length less than (\d+)', 'max_length'),
            (r'fewer than (\d+) characters', 'max_length'),
            (r'exactly (\d+) characters', 'min_length', 'max_length'),
        ]
        
        # Apply keyword mappings
        for keyword, filters in keyword_mappings.items():
            if keyword in query:
                parsed_filters.update(filters)
        
        # Apply length patterns
        for pattern, *filter_types in length_patterns:
            matches = re.search(pattern, query)
            if matches:
                length_value = int(matches.group(1))
                for filter_type in filter_types:
                    if filter_type == 'min_length':
                        parsed_filters['min_length'] = length_value + 1
                    elif filter_type == 'max_length':
                        parsed_filters['max_length'] = length_value - 1
                    else:
                        parsed_filters['min_length'] = length_value
                        parsed_filters['max_length'] = length_value
        
        # Word count patterns
        word_count_pattern = r'(\d+) words?'
        word_matches = re.search(word_count_pattern, query)
        if word_matches:
            parsed_filters['word_count'] = int(word_matches.group(1))
        
        return parsed_filters