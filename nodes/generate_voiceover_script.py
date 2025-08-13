# nodes/generate_instagram_script.py
from textwrap import dedent
from state import NewsAgentState
from openai import OpenAI
import os
from datetime import datetime,timezone
from dotenv import load_dotenv

SCRIPT_PROMPT_TMPL = """You are the narrator for "Tech Brief AI" — a daily Instagram reel delivering 5 tech headlines in under 60 seconds.

Your job: Combine the following 5 short summaries into ONE continuous voiceover script for ElevenLabs input.

Guidelines:
- Tone: Conversational, friendly, confident — like you’re talking to a friend who loves tech.
- Style: Short sentences. Clear and punchy.
- Flow: Use smooth transitions like "Next up..." or "In other news..."
- Length: 40–60 seconds total (~150–180 words). Stay under 180 words.
- End with: "Follow Tech Brief AI for tomorrow’s top tech stories."
- No robotic phrasing or filler words.
- No long intros — jump straight into the first headline.

Here are today’s summaries:
{summaries_block}

Return only the final script, no preamble.
"""


load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))  


def make_summaries_block(summaries: list[str]) -> str:
    # Preface each for rhythm; summaries already short
    lines = []
    for i, s in enumerate(summaries[:5], 1):
        lines.append(f"{i}. {s.strip()}")
    return "\n".join(lines)


def generate_instagram_script(state: NewsAgentState) -> NewsAgentState:
    if not state.summaries or len(state.summaries) < 3:
        raise ValueError("Need 3 summaries to build the Instagram script.")

    prompt = SCRIPT_PROMPT_TMPL.format(
        summaries_block=make_summaries_block(state.summaries)
    )

    response = client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-3.5-turbo"
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
    if response.choices[0].message.content is None:
            raise ValueError("Error retrieving response")

    scriptGenerated = response.choices[0].message.content.strip()
    write_script_to_file(scriptGenerated)
    state.script_text = scriptGenerated
    print("📝 Instagram script ready.")
    return state

def write_script_to_file(script_text: str) -> str:
    out_dir = os.getenv("SCRIPT_OUTPUT_DIR", "output")
    os.makedirs(out_dir, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")  
    filename = f"{date_str}_tech_brief_ai_script.txt"
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(script_text)
    return path
