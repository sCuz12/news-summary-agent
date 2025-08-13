
from typing import List
from playwright.sync_api import Page
from state import Article
from .base import BaseScraper
from bs4 import BeautifulSoup

class Business_Insider(BaseScraper):
    def matches(self,url : str) -> bool:
        return "businessinsider" in url

    def scrape(self, url: str, page: Page) -> List[Article]:
        print("📡 Scraping TechCrunch...")
        page.goto(url, timeout=30000)
        page.wait_for_selector("article", timeout=10000)
        
        articles : List[Article] = []

        article_elements = page.locator("article")

        count = article_elements.count()
        print(f"🧠 Found {count} articles on Business Insider")
        article_urls = self.extract_article_urls(page)

        for link in article_urls:
            try:
                page.goto(link, timeout=20000)
                page.wait_for_selector("article", timeout=8000)

                title = page.title().strip()

                # Extract raw HTML from the article body
                html = page.inner_html("article")

                # Use BeautifulSoup to clean it
                soup = BeautifulSoup(html, "html.parser")
                paragraphs = soup.select("div.article-content p")

                content = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

                if not content or len(content) < 200:
                    print(f"⚠️ Skipping due to short content: {link}")
                    continue

                articles.append(Article(
                    title=title,
                    url=link,
                    content=content
                ))

            except Exception as e:
                print(f"❌ Failed to scrape {link}: {e}")
                continue 
            try:
                page.goto(link, timeout=20000)
                page.wait_for_selector("article", timeout=8000)

                title = page.title()
                paragraphs = page.inner_html(".post-body-content")
                # content = "\n".join(
                #     [paragraphs.nth(j).inner_text() for j in range(paragraphs.count())]
                # )
                # print(content)
                print(paragraphs)

                articles.append(Article(
                    title=title.strip(),
                    url=link,
                    content="Test"
                ))

            except Exception as e:
                print(f"❌ Failed to scrape {link}: {e}")
                continue
            
        print(articles)
        raise ValueError('asdas')
        return articles  

    def extract_article_urls(self, page: Page) -> List[str]:
        page.wait_for_selector("a.tout-title-link", timeout=10000)

        urls = page.eval_on_selector_all(
            "a.tout-title-link",
            """(links) => links
                .map(link => link.href)
                .filter(href => href.includes('/'))  // avoid junk
                .slice(0, 5)"""
        )

        full_urls = [
            url if url.startswith("http") else f"https://www.businessinsider.com{url}"
            for url in urls
        ]
        return full_urls
        