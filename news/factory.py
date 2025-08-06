from .cyprus_mail import CyprusMailScraper
from .techcrunch import TechCrunchScraper
from .base import BaseScraper
from typing import List

SCRAPERS: List[BaseScraper] = [
    CyprusMailScraper(),
    TechCrunchScraper(),
    # Add TechCrunchScraper, VergeScraper, etc. here
]

def get_scraper_for_url(url: str) -> BaseScraper:
    for scraper in SCRAPERS:
        if scraper.matches(url):
            return scraper
    raise ValueError("no scrapper found")