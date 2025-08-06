# nodes/send_email.py

from state import NewsAgentState
from postmarker.core import PostmarkClient

def format_email_body(state: NewsAgentState) -> str:
    body = f"🗞️ Daily Digest for topic: {state.topic.title()}\n\n"

    for i, summary in enumerate(state.summaries):
        article = state.articles[i]
        body += f"🔹 **{article.title}**\n{summary}\n🔗 {article.url}\n\n"

    return body

def send_email(state: NewsAgentState) -> NewsAgentState:
    pClient = PostmarkClient(server_token="6aed2c54-6974-49ee-850e-32b74e57c2d3")

    html = f"<h2>🧠 Daily Digest: {state.topic.title()}</h2>"
    for article, summary in zip(state.articles, state.summaries):
            html += f"""
            <h3>{article.title}</h3>
            <p>{summary}</p>
            <p><a href="{article.url}">Read full article</a></p>
            <hr>
        """
            
    pClient.emails.send( # type: ignore[attr-defined]
        From='george.hadjisavva@avocadots.com',
        To='georgex8@gmail.com',
        Subject="Daily News Insights",
        HtmlBody=html
        )

    print("✅ Email sent successfully.")
    return state
