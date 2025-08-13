# utils/helper.py
import json
import os
from pathlib import Path

# Location to persist seen URLs between runs
SEEN_URLS_FILE = Path(".seen_urls.json")

# Load into memory on first import
_seen_urls = set()

if SEEN_URLS_FILE.exists():
    try:
        with open(SEEN_URLS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                _seen_urls = set(data)
    except Exception as e:
        print(f"⚠️ Failed to load seen URLs: {e}")


def is_url_seen(url: str) -> bool:
    """Return True if the URL has been seen before."""
    return url in _seen_urls


def mark_url_as_seen(url: str) -> None:
    """Mark a URL as seen and persist the store to disk."""
    _seen_urls.add(url)
    _save_seen_urls()


def _save_seen_urls() -> None:
    try:
        with open(SEEN_URLS_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted(_seen_urls), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ Failed to save seen URLs: {e}")


def clear_seen_urls() -> None:
    """Clear all stored URLs (useful for dev/testing)."""
    _seen_urls.clear()
    _save_seen_urls()
