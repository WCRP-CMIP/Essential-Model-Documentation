"""
Generate @id from issue submitter and creation timestamp
"""

from datetime import datetime
import hashlib


def timestamp_to_epoch(timestamp_str):
    """
    Convert ISO 8601 timestamp to seconds since epoch.
    
    Args:
        timestamp_str: ISO 8601 format string (e.g., '2025-02-26T15:30:45Z')
    
    Returns:
        Integer seconds since epoch
    """
    if not timestamp_str:
        return None
    
    try:
        # Parse ISO 8601 format
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return int(dt.timestamp())
    except (ValueError, AttributeError):
        return None


def generate_id_from_issue(author, created_at):
    """
    Generate a unique @id from issue submitter and timestamp.
    
    Args:
        author: GitHub username (string)
        created_at: ISO 8601 timestamp string (e.g., '2025-02-26T15:30:45Z')
    
    Returns:
        Dictionary with:
        - 'author': the submitter username
        - 'epoch': seconds since epoch
        - 'id': generated ID (author-epoch or hash-based)
    """
    
    epoch = timestamp_to_epoch(created_at)
    
    if not author:
        return {
            'author': 'unknown',
            'epoch': epoch,
            'id': f'unknown-{epoch}' if epoch else 'unknown'
        }
    
    if epoch:
        return {
            'author': author,
            'epoch': epoch,
            'id': f'{author}-{epoch}'
        }
    else:
        # Fallback to hash if timestamp can't be parsed
        hash_str = hashlib.md5(f"{author}{created_at}".encode()).hexdigest()[:8]
        return {
            'author': author,
            'epoch': None,
            'id': f'{author}-{hash_str}'
        }


def clean_id(id_str):
    """Clean an ID to be URL-safe"""
    if not id_str:
        return ''
    return id_str.lower().strip().replace(' ', '-').replace('_', '-')
