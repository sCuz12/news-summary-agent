from .cyprus_mail import CyprusMailScraper
from .techcrunch import TechCrunchScraper
from .business_insider import Business_Insider
from .base import BaseScraper
from typing import List

SCRAPERS: List[BaseScraper] = [
    CyprusMailScraper(),
    TechCrunchScraper(),
    Business_Insider(),
    # Add TechCrunchScraper, VergeScraper, etc. here
]

def get_scraper_for_url(url: str) -> BaseScraper:
    for scraper in SCRAPERS:
        if scraper.matches(url):
            return scraper
    raise ValueError("no scrapper found")