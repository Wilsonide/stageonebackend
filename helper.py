import hashlib
from collections import Counter

from config import config


def analyze_string(s: str):
    """
    Analyze a given string and return a dictionary with the following properties.

      - length: total number of characters
      - is_palindrome: whether the string reads the same forwards and backwards (case-insensitive)
      - unique_characters: count of distinct characters
      - word_count: number of words separated by whitespace
      - sha256_hash: SHA-256 hash of the string
      - character_frequency_map: dictionary mapping each character to its occurrence count.
    """
    # Normalize string for palindrome check
    normalized = "".join(ch.lower() for ch in s if not ch.isspace())
    is_palindrome = normalized == normalized[::-1]

    # Character frequency map
    char_freq = dict(Counter(s))

    # SHA-256 hash
    sha256_hash = hashlib.sha256(s.encode("utf-8")).hexdigest()

    return {
        "length": len(s),
        "is_palindrome": is_palindrome,
        "unique_characters": len(set(s)),
        "word_count": len(s.split()),
        "sha256_hash": sha256_hash,
        "character_frequency_map": char_freq,
    }


def parse_natural_query(query: str) -> dict:
    filters = {}
    if not query:
        return filters

    q = query.lower()

    # Don't return immediately for 'all', just skip
    # if "all" in q:
    #     return filters

    # palindrome
    if "palindrome" in q or "palindromic" in q:
        filters["is_palindrome"] = True
    elif "not palindrome" in q or "not palindromic" in q:
        filters["is_palindrome"] = False

    # word count
    if "single word" in q or "one word" in q:
        filters["word_count"] = 1
    elif "two words" in q or "2 words" in q:
        filters["word_count"] = 2

    # contains character
    if "contains" in q:
        parts = q.split("contains")
        if len(parts) > 1:
            ch = parts[1].strip().split()[0]
            if ch:
                filters["contains_character"] = ch

    return filters


def parse_query(query: str):
    filters = {}
    if not query:
        return filters

    parts = query.split("&")
    for part in parts:
        if "=" in part:
            key, value = part.split("=", 1)

            # convert types properly
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif value.isdigit():
                value = int(value)

            filters[key] = value
    return filters
