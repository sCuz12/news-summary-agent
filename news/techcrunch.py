# news/scraper/techcrunch.py
from .base import BaseScraper
from playwright.sync_api import Page
from state import Article
from bs4 import BeautifulSoup
from typing import List
import random
import os
from utils.helper import download_image 

ASSETS_DIR = os.getenv('ASSETS_DIR',"assets")
class TechCrunchScraper(BaseScraper):
    def matches(self, url: str) -> bool:
        return "techcrunch.com" in url

    def scrape(self, url: str, page: Page) -> List[Article]:
        print("📡 Scraping TechCrunch...")

        page.goto("https://techcrunch.com/latest/", timeout=60000)
        page.wait_for_selector(".loop-card__title-link", timeout=15000)

        urls = page.eval_on_selector_all(
            ".loop-card",
            """(cards) => cards.slice(0, 8).map(card => {
                const link = card.querySelector(".loop-card__title-link");
                const url = link?.href;
                return url;
            }).filter(Boolean)"""
        )

        random.shuffle(urls)

        articles = []

        for url in urls[:5]:
            try:
                page.goto(url, timeout=30000)

                # Optional: accept cookies
                try:
                    page.click('text="Consent"', timeout=3000)
                except:
                    pass

                content_html = page.inner_html('.entry-content.wp-block-post-content-is-layout-constrained')
                soup = BeautifulSoup(content_html, 'html.parser')

                banner = page.locator("figure.wp-block-post-featured-image img")
                image_src = banner.get_attribute("src")
                #download the image to folder
                if isinstance(image_src,str):
                    download_image(image_src,ASSETS_DIR)

                title = page.title()
                full_text = "\n".join(p.get_text(strip=True) for p in soup.find_all('p'))

                articles.append(Article(
                    title=title.strip(),
                    url=url,
                    content=full_text
                ))
            except Exception as e:
                print(f"⚠️ Skipped article {url} due to error: {e}")
                continue

        exit()
        return articles
