#!/usr/bin/env python3
"""
JSON sanitization utilities for EMD data processing.

Provides functions to escape control characters in JSON before parsing,
preventing jq and graphify validation errors.
"""

import json
from pathlib import Path


def sanitize_json_string(text: str) -> str:
    """
    Escape control characters (U+0000-U+001F) in a JSON string.
    
    These characters must be escaped in JSON according to RFC 7159.
    This function converts literal control characters to their escape sequences.
    
    Args:
        text: Raw JSON string that may contain unescaped control characters
        
    Returns:
        JSON string with all control characters properly escaped
    """
    result = []
    for char in text:
        code = ord(char)
        if 0 <= code <= 0x1F:  # Control characters U+0000 through U+001F
            if char == '\n':
                result.append('\\n')
            elif char == '\t':
                result.append('\\t')
            elif char == '\r':
                result.append('\\r')
            elif char == '\b':
                result.append('\\b')
            elif char == '\f':
                result.append('\\f')
            else:
                # Other control chars: escape as \uXXXX
                result.append(f'\\u{code:04x}')
        else:
            result.append(char)
    return ''.join(result)


def load_json_safe(path: str | Path) -> dict:
    """
    Load a JSON file, sanitizing control characters before parsing.
    
    Args:
        path: Path to the JSON file
        
    Returns:
        Parsed JSON object
        
    Raises:
        json.JSONDecodeError: If JSON is invalid after sanitization
        FileNotFoundError: If file does not exist
    """
    with open(path, encoding='utf-8') as f:
        text = f.read()
    text = sanitize_json_string(text)
    return json.loads(text)


def save_json_safe(path: str | Path, data: dict) -> None:
    """
    Save a JSON object to file with proper formatting.
    
    Args:
        path: Path where JSON should be written
        data: Dictionary to serialize
    """
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
        f.write('\n')
