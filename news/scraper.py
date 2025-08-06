
from playwright.sync_api import sync_playwright
from typing import List, Dict
from state import Article
from news.factory import get_scraper_for_url

def fetch_articles(sources: List[str]) -> List[Article]:
    print("🕷 Fetching articles...")
    all_articles = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for url in sources:
            scraper = get_scraper_for_url(url)
            if not scraper:
                print(f"⚠️ No scraper found for URL: {url}")
                continue

            print(f"📄 Using scraper: {scraper.__class__.__name__}")
            articles = scraper.scrape(url, page)
            all_articles.extend(articles)

        browser.close()

    return all_articles 