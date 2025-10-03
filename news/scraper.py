from playwright.sync_api import sync_playwright
from typing import List,Set
from state import Article
from news.factory import get_scraper_for_url
from utils.helper import is_url_seen,mark_url_as_seen
import os


MIN_TOTAL_ARTICLES = int(os.getenv("MIN_TOTAL_ARTICLES", "5"))
MAX_PASSES = int(os.getenv("MAX_PASSES", "2"))

def fetch_articles(sources: List[str]) -> List[Article]:
    print("🕷 Fetching articles...")
    all_articles: List[Article] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        passes = 0
        while passes < MAX_PASSES and len(all_articles) < MIN_TOTAL_ARTICLES:
            passes += 1
            for url in sources:
                if len(all_articles) >= MIN_TOTAL_ARTICLES:
                    break

                scraper = get_scraper_for_url(url)
                if not scraper:
                    print(f"⚠️ No scraper found for URL: {url}")
                    continue

                print(f"📄 Using scraper: {scraper.__class__.__name__} (pass {passes})")
                try:
                    scraped = scraper.scrape(url, page)
                except Exception as e:
                    print(f"❌ Scraper failed for {url}: {e}")

                # final dedupe + mark as seen only after we accept it
                for article in scraped:
                    if is_url_seen(article.url):
                        print(f"⏭ Skipping seen article: {article.url}")
                        continue
                    mark_url_as_seen(article.url)
                    all_articles.append(article)
                    if len(all_articles) >= MIN_TOTAL_ARTICLES:
                        break

        browser.close()

    print(f"✅ Collected {len(all_articles)} articles")
    print(f"articles")
    return all_articles