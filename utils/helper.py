# utils/helper.py
import json
import os
from pathlib import Path
import os, re, time, random, hashlib, requests
from urllib.parse import urljoin, urlparse

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
import os
from datetime import datetime, timezone

def save_text_to_file(path: str, text: str) -> str:
    """
    Save text content to a file, ensuring directories exist.

    Args:
        path (str): Full file path, e.g. "output/descriptions/social/tiktok/name.txt"
        text (str): Content to write

    Returns:
        str: The full path of the saved file
    """
    # Ensure parent directories exist
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Write content
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.strip())

    print(f"✅ Saved file at {path}")
    return path

def download_image(url: str, dest_dir: str) -> str:
    today = datetime.now()
    datestring = today.strftime("%Y-%m-%d")
    dest_dir = os.path.join(dest_dir,datestring)
    os.makedirs(dest_dir, exist_ok=True)
    try:
        r = requests.get(url, timeout=10, stream=True, headers={"User-Agent":"TechBriefBot/1.0"})
        ct = r.headers.get("content-type","").lower()
        if r.status_code != 200 or "image" not in ct:
            return ""
        data = r.content
        h = hashlib.sha1(data).hexdigest()[:12]
        ext = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp"
        }.get(ct.split(";")[0], os.path.splitext(urlparse(url).path)[1] or ".jpg")
        path = os.path.join(dest_dir, f"img_{h}{ext}")
        with open(path, "wb") as f:
            f.write(data)
        return path
    except Exception:
        return ""