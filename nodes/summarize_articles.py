# nodes/summarize_articles.py

from state import NewsAgentState
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))  

def summarize_articles(state: NewsAgentState) -> NewsAgentState:
    print(f"🧠 Summarizing {len(state.articles)} articles...")

    summaries = []

    for article in state.articles:
        prompt = (
            "You're an assistant helping someone stay informed via a daily digest.\n"
            "Summarize the following news article in 5-6 sentences.\n"
            "Highlight the key takeaway, and if possible, include why it might matter or be useful for someone staying aware of important developments.\n\n"
            f"Title: {article.title}\n"
            f"Content: {article.content}\n\n"
            "Summary:"
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-3.5-turbo"
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        if response.choices[0].message.content is None:
            raise ValueError("Error retrieving response")

        summary = response.choices[0].message.content.strip()
        summaries.append(summary)

    state.summaries = summaries
    print(state.summaries)
    return state
