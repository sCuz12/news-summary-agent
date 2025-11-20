# nodes/summarize_articles.py

from state import NewsAgentState
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))  


def summarize_articles(state: NewsAgentState) -> NewsAgentState:
    print(f"🧠 Summarizing {len(state.articles)} articles...")

    summaries = []

    for article in state.articles:
        prompt = (
            "You are an assistant writing short, spoken-style tech news recaps for a daily AI-powered video brief.\n"
            "Summarize the article below in 3–4 short sentences (max 100-120 words).\n"
            "Each sentence should sound natural when spoken — conversational, energetic, and clear.\n"
            "Focus on what happened, who’s involved, and why it matters to the audience.\n"
            "Use strong verbs and emotional color when appropriate (e.g., 'shocked', 'surprised', 'bold move').\n"
            "Avoid jargon or filler. Keep sentences punchy and rhythmic, like a TikTok/Instagram tech host talking to camera.\n"
            "If there's a twist, hint at it (‘but here’s the catch...’).\n\n"
            f"Title: {article.title}\n"
            f"Content: {article.content}\n\n"
            "Spoken Summary:"
        )

        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL","gpt-4o-mini"), 
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
