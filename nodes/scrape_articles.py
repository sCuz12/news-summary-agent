
from state import NewsAgentState
from news.scraper import fetch_articles


# --- Define LangGraph node ---
def scrape_articles(state: NewsAgentState) -> NewsAgentState:
    print(f"🔍 Scraping sources: {state.sources}")
    state.articles = fetch_articles(state.sources)

    return state