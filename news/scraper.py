
from playwright.sync_api import sync_playwright
from typing import List, Dict
from state import Article
from news.factory import get_scraper_for_url
from utils.helper import is_url_seen,mark_url_as_seen


from playwright.sync_api import sync_playwright
from typing import List, Dict
from state import Article
from news.factory import get_scraper_for_url
from utils.helper import is_url_seen,mark_url_as_seen

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
            try:
                scraped = scraper.scrape(url, page)
            except Exception as e:
                print(f"❌ Scraper failed for {url}: {e}")
                continue

            #dedup
            for article in scraped:
                if is_url_seen(article.url):
                    print(f"⏭ Skipping seen article: {article.url}")
                    continue
                mark_url_as_seen(article.url)
                all_articles.append(article)
        browser.close()
    return all_articles 