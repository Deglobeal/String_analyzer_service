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
    
    # SHA256 hash - MUST use UTF-8 encoding
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
    """Parse natural language query into filters using keyword detection."""
    query = query.lower().strip()
    filters = {}
    
    print(f"🔍 Parsing query: '{query}'")  # Debug
    
    # Word count detection
    if "single word" in query or "one word" in query:
        filters['word_count'] = 1
        print("  → Detected: word_count = 1")
    
    if "two words" in query:
        filters['word_count'] = 2
        print("  → Detected: word_count = 2")
    
    if "three words" in query:
        filters['word_count'] = 3
        print("  → Detected: word_count = 3")
    
    # Palindrome detection
    if "palindromic" in query or "palindrome" in query:
        filters['is_palindrome'] = True
        print("  → Detected: is_palindrome = True")
    
    # Length filters
    if "longer than" in query or "greater than" in query:
        # Extract number after "longer than" or "greater than"
        match = re.search(r'(?:longer than|greater than)\s+(\d+)', query)
        if match:
            min_length = int(match.group(1))
            filters['min_length'] = min_length + 1
            print(f"  → Detected: min_length = {min_length + 1}")
    
    if "shorter than" in query or "less than" in query:
        # Extract number after "shorter than" or "less than"
        match = re.search(r'(?:shorter than|less than)\s+(\d+)', query)
        if match:
            max_length = int(match.group(1))
            filters['max_length'] = max_length - 1
            print(f"  → Detected: max_length = {max_length - 1}")
    
    # Character containment
    if "containing the letter" in query:
        match = re.search(r'containing the letter\s+([a-zA-Z])', query)
        if match:
            filters['contains_character'] = match.group(1).lower()
            print(f"  → Detected: contains_character = '{match.group(1).lower()}'")
    
    if "containing the letter" not in query and "contain" in query:
        # Look for pattern like "contains a" or "containing e"
        match = re.search(r'contain[s]?[\w\s]*([a-zA-Z])', query)
        if match:
            filters['contains_character'] = match.group(1).lower()
            print(f"  → Detected: contains_character = '{match.group(1).lower()}'")
    
    # First vowel detection
    if "first vowel" in query:
        filters['contains_character'] = 'a'
        print("  → Detected: first vowel → contains_character = 'a'")
    
    # Specific vowel detection
    vowel_mapping = {
        'vowel a': 'a',
        'vowel e': 'e', 
        'vowel i': 'i',
        'vowel o': 'o',
        'vowel u': 'u'
    }
    
    for vowel_pattern, vowel_char in vowel_mapping.items():
        if vowel_pattern in query:
            filters['contains_character'] = vowel_char
            print(f"  → Detected: {vowel_pattern} → contains_character = '{vowel_char}'")
            break
    
    print(f"  → Final filters: {filters}")
    return filters