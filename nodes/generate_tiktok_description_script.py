from state import NewsAgentState
from openai import OpenAI
from utils.helper import save_text_to_file
import os, time



client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TIKTOK_PROMPT = """You are writing a TikTok video caption for a daily tech news reel.

Guidelines:
- Tone: punchy, modern, trend-friendly.
- Keep it under 100 characters.
- Use emojis naturally (⚡, 📱, 🤖, 🚀, etc).
- Add 3–4 relevant trending hashtags (e.g., #TechNews, #AI, #Startups, #Innovation).
- No hashtags in the middle of the sentence; put them at the end.
- Make it feel like a hook, not a summary.

Script:
{script_text}

Return only the caption text.
"""

DESCRIPTIONS_PATH = "output/descriptions/social/tiktok/daily_caption.txt" 

def _generate_with_retries(messages, model="gpt-4o-mini", temperature=0.6, max_attempts=1):
    backoff = 1.0
    last_err = None
    for _ in range(max_attempts):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
            content = (resp.choices[0].message.content or "").strip()
            if content:
                return content
            last_err = ValueError("Empty content.")
        except Exception as e:
            last_err = e
        time.sleep(backoff)
        backoff *= 1.7
    raise RuntimeError(f"OpenAI completion failed after retries: {last_err}")

def generate_tiktok_description(state: NewsAgentState) : 
    print("Generating TIKTOK media descriptions")
    if not state.script_text:
        raise ValueError("script text is missing")

    prompt = TIKTOK_PROMPT.format(script_text=state.script_text)

    caption = _generate_with_retries(
        messages=[{"role":"user","content":prompt}],
                                     model=os.getenv("OPENAI_MODEL","gpt-4o-mini"),
                                     temperature=0.6)
    
    state.descriptions = getattr(state,"descriptions",{})
    state.descriptions["tiktok"] = caption

    save_text_to_file(DESCRIPTIONS_PATH,caption)




