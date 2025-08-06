from abc import ABC, abstractmethod
from playwright.sync_api import Page
from state import Article
from typing import List

class BaseScraper(ABC):
    @abstractmethod
    def matches(self, url: str) -> bool:
        pass

    @abstractmethod
    def scrape(self, url: str, page: Page) -> List[Article]:
        pass