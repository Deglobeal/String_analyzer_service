import hashlib
import re
from collections import Counter
from typing import Dict, Any

def compute_string_properties(value: str) -> Dict[str, Any]:
    """Compute all properties for a given string."""
    
    # Basic properties
    length = len(value)
    
    # Palindrome check (case-insensitive) - only consider alphanumeric characters
    cleaned_value = re.sub(r'[^a-zA-Z0-9]', '', value.lower())
    is_palindrome = cleaned_value == cleaned_value[::-1] if cleaned_value else False
    
    # Unique characters count
    unique_characters = len(set(value))
    
    # Word count (split by whitespace)
    word_count = len(value.split())
    
    # SHA256 hash
    sha256_hash = hashlib.sha256(value.encode('utf-8')).hexdigest()
    
    # Character frequency map
    character_frequency_map = dict(Counter(value))
    
    return {
        'length': length,
        'is_palindrome': is_palindrome,
        'unique_characters': unique_characters,
        'word_count': word_count,
        'sha256_hash': sha256_hash,
        'character_frequency_map': character_frequency_map
    }

def parse_natural_language_query(query: str) -> Dict[str, Any]:
    """Parse natural language query into filters."""
    filters = {}
    query = query.lower()
    
    # Parse word count
    if 'single word' in query :
        filters['word_count'] = 1
    elif 'two words' in query:
        filters['word_count'] = 2
    elif 'three words' in query:
        filters['word_count'] = 3
    
    # Parse palindrome
    if 'palindromic' in query or 'palindrome' in query:
        filters['is_palindrome'] = True
    
    # Parse length filters
    if 'longer than' in query:
        match = re.search(r'longer than\s+(\d+)', query)
        if match:
            filters['min_length'] = int(match.group(1)) + 1
    elif 'shorter than' in query:
        match = re.search(r'shorter than\s+(\d+)', query)
        if match:
            filters['max_length'] = int(match.group(1)) - 1
    elif 'length' in query and 'greater' in query:
        match = re.search(r'greater than\s+(\d+)', query)
        if match:
            filters['min_length'] = int(match.group(1)) + 1
    elif 'length' in query and 'less' in query:
        match = re.search(r'less than\s+(\d+)', query)
        if match:
            filters['max_length'] = int(match.group(1)) - 1
    
    # Parse character containment
    char_match = re.search(r'contain[s]?\s+the letter\s+([a-zA-Z])', query)
    if not char_match:
        char_match = re.search(r'contain[s]?\s+([a-zA-Z])', query)
    if not char_match:
        char_match = re.search(r'with the letter\s+([a-zA-Z])', query)
    if char_match:
        filters['contains_character'] = char_match.group(1).lower()
    
    # Handle vowel detection
    if 'first vowel' in query or 'vowel a' in query:
        filters['contains_character'] = 'a'
    elif 'vowel e' in query:
        filters['contains_character'] = 'e'
    elif 'vowel i' in query:
        filters['contains_character'] = 'i'
    elif 'vowel o' in query:
        filters['contains_character'] = 'o'
    elif 'vowel u' in query:
        filters['contains_character'] = 'u'
    
    # Handle "all" queries
    if 'all strings' in query and not filters:
        # Return empty filters to get all strings
        pass
    
    return filters