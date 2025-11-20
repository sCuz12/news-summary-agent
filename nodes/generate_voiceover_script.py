# nodes/generate_instagram_script.py
from __future__ import annotations
from textwrap import dedent
from state import NewsAgentState
from openai import OpenAI
import os, random, time, re
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model  = os.getenv("OPENAI_MODEL")

# ===== Prosody-aware building blocks =====
HOOKS = [
    "Coffee in hand? Let’s fly through today’s tech in under a minute.",
    "Blink and you’ll miss it—here are the 5 biggest tech moves today.",
    "Quick hit of tech you can actually use—ready?",
    "Your 60-second tech upgrade starts now.",
]

TRANSITIONS = [
    "Next up—", "Meanwhile—", "In other news—", "Also—", "And finally—"
]

CTAS = [
    "Follow Tech Brief AI for tomorrow’s top tech stories.",
    "Tap follow for your daily 60-second tech brief.",
    "Follow Tech Brief AI—back tomorrow with the need-to-know.",
    "Hit follow so you never miss the daily tech rundown."
]

STYLE_PRESETS = {
    # Uses punctuation and rhythm TTS respects (commas, em dashes, ellipses, short lines).
    "punchy": dict(
        sentence_max=18,
        wpm=165,   # rough pacing check
        temperature=0.5
    ),
    "warm": dict(
        sentence_max=22,
        wpm=155,
        temperature=0.6
    ),
    "newswire": dict(
        sentence_max=20,
        wpm=175,
        temperature=0.3
    ),
}

SCRIPT_PROMPT_TMPL = """You are the narrator for "Tech Brief AI" — a daily short-form tech news brief.

Write ONE continuous voiceover script optimized for TikTok/Instagram/YouTube Shorts and ElevenLabs natural speech synthesis.

Rules for structure and flow:
- There are exactly {headline_count} headlines.
- Use transitions *in order*: 
  - Between story 1→2: "Next up—"
  - Between story 2→3: "Meanwhile—"
  - Between story 3→4: "Also—"
  - Before the last story: "Finally—"
- Start with a BOLD HOOK under 10 words that sparks curiosity.
- Each headline gets 2–3 short sentences: what happened, who’s involved, why it matters.
- Tone: conversational, confident, slightly witty — like a sharp TikTok news host.
- Keep sentences 6–12 words max. Use commas, em dashes, ellipses, or rhetorical questions for rhythm.
- Use strong but varied emotion words (surprising, bold, clever, dramatic, unexpected).
- Add one micro-cliffhanger or “but here’s the twist…” per story.
- Stay under 165 words total.
- End with the daily CTA: “Follow techbrief.ai — 5 stories, 60 seconds. Coffee ready?”

Headlines:
{summaries_block}

Return only the narration text. No preamble, numbering, or quotes.
"""

def make_summaries_block(summaries: list[str]) -> str:
    # Keep them tight and dedup very similar lines
    seen = set()
    clean = []
    for s in summaries[:5]:
        t = re.sub(r"\s+", " ", s).strip()
        if t and t.lower() not in seen:
            seen.add(t.lower())
            clean.append(t)
    return "\n".join(f"- {s}" for s in clean)

def _count_words(text: str) -> int:
    return len(re.findall(r"\w+", text))


def _postprocess_for_tts(text: str) -> str:
    # Normalize spaces, ensure readable line breaks for breath points
    text = re.sub(r"\s+", " ", text).strip()
    # Add soft breaks after transitions/em-dashes
    text = text.replace("— ", "— ")
    # Optional: insert line breaks after ~3 sentences to help pacing in editors
    sentences = re.split(r"(?<=[.!?])\s+", text)
    blocks, buf, count = [], [], 0
    for s in sentences:
        buf.append(s)
        count += 1
        if count >= 3:
            blocks.append(" ".join(buf))
            buf, count = [], 0
    if buf:
        blocks.append(" ".join(buf))
    return "\n".join(blocks)

def _compose_user_prompt(summaries_block: str,headline_counts: int) -> str:
    return SCRIPT_PROMPT_TMPL.format(summaries_block=summaries_block,headline_count=headline_counts)

def _generate_with_retries(messages, model="gpt-4o-mini", temperature=0.5, max_attempts=3):
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


def write_script_to_file(script_text: str) -> str:
    out_dir = os.getenv("SCRIPT_OUTPUT_DIR", "output")
    os.makedirs(out_dir, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f"{date_str}_tech_brief_ai_script.txt"
    path = os.path.join(out_dir, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(script_text)
    return path

def generate_instagram_script(state: NewsAgentState, style: str = "punchy") -> NewsAgentState:
    summaries_count = len(state.summaries)

    if not state.summaries or summaries_count < 3:
        raise ValueError("Need at least 3 summaries to build the Instagram script.")

    preset = STYLE_PRESETS.get(style, STYLE_PRESETS["punchy"])

    prompt = _compose_user_prompt(make_summaries_block(state.summaries),summaries_count)

    # Generate two takes; pick the one closest to 165 words
    takes = []
    for _ in range(2):
        raw = _generate_with_retries(
            messages=[{"role": "user", "content": prompt}],
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=float(os.getenv("SCRIPT_TEMPERATURE", preset["temperature"])),
        )
        # candidate = _inject_hook_transitions_cta(raw, hook, cta)
        candidate = _postprocess_for_tts(raw)
        takes.append(candidate)

    # Choose the take whose length (in words) is closest to target window center (≈165 words)
    target = 165
    best = min(takes, key=lambda t: abs(_count_words(t) - target))

    path = write_script_to_file(best)
    state.script_text = best
    print(f"📝 Instagram script ready. Words={_count_words(best)} | Style={style}")
    return state
