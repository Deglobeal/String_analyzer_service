# strings/utils.py
import hashlib
import re
from collections import Counter

def compute_properties(value: str) -> dict:
    if not isinstance(value, str):
        raise TypeError("value must be a string")

    # preserve original string for output but computations are case-insensitive for palindrome
    normalized = value
    length = len(normalized)
    # palindrome check: remove whitespace? The spec: "case-insensitive", not necessarily remove spaces.
    # We'll do case-insensitive and ignore surrounding whitespace, but keep internal spaces (common expectation).
    normalized_for_pal = normalized.strip().lower()
    is_palindrome = normalized_for_pal == normalized_for_pal[::-1]
    # unique characters (distinct code points)
    unique_characters = len(set(normalized))
    # word count: split on any whitespace
    word_count = 0 if normalized.strip() == "" else len(re.findall(r"\S+", normalized))
    # sha256
    sha256_hash = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    # frequency map (character by character, keep case as-is)
    freq = dict(Counter(normalized))
    return {
        "length": length,
        "is_palindrome": is_palindrome,
        "unique_characters": unique_characters,
        "word_count": word_count,
        "sha256_hash": sha256_hash,
        "character_frequency_map": freq,
    }
