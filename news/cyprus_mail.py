from .base import BaseScraper
from playwright.sync_api import Page
from state import Article
from typing import List

class CyprusMailScraper(BaseScraper):
    def matches(self, url: str) -> bool:
        return "cyprus-mail.com" in url

    def scrape(self, url: str, page: Page) -> List[Article]:
        page.goto(url, timeout=30000)

        articles = []
        article_elements = page.locator("article")
        count = article_elements.count()

        for i in range(min(count, 5)):
            article = article_elements.nth(i)
            title = article.locator("h2._articleTitle_cekga_5").inner_text()
            raw_href = article.locator("a._lnkTitle_cekga_5").get_attribute("href")
            if not raw_href:
                continue

            link = f"https://cyprus-mail.com{raw_href}" if raw_href.startswith("/") else raw_href
            page.goto(link)
            page.wait_for_timeout(1000)

            paragraphs = page.locator("div#articleBody p")
            full_content = "\n".join([paragraphs.nth(j).inner_text() for j in range(paragraphs.count())])

            articles.append(Article(title=title.strip(), url=link, content=full_content))

        return articles