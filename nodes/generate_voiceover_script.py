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

SCRIPT_PROMPT_TMPL = """You are the narrator for "Tech Brief AI" — daily 5 tech headlines in under 60 seconds.

Write ONE continuous voiceover script for ElevenLabs using the items below.

Hard rules (optimize for hooks & retention):
- Start with a *punchy HOOK* as a single short line: a bold claim or provocative question that teases stakes (e.g., “Apple just changed everything.” / “What if search died today?”).
- Immediately jump into headline 1. No setup, no greeting.
- Within the first two lines, *tease a surprise at the end* (“…and the last one’s wild.”) to keep viewers watching.
- Tone: conversational, confident, modern.
- Sentences: short and punchy. Prefer commas, em dashes, ellipses for rhythm.
- Transitions: vary them (“Next up—”, “Meanwhile—”, “Also—”, “Finally—”).
- Keep total length 150–175 words (never exceed 180). No lists or numbering; make it flow.
- Do NOT include bracketed stage directions or speaker labels.
- End with a sharp CTA that reinforces the brand ritual: “Follow @techbrief.ai — 5 stories, 60 seconds. Coffee ready?”

Headlines:
{summaries_block}

Return only the script text. No preamble, no numbering, no quotes.
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

def _compose_user_prompt(summaries_block: str) -> str:
    return SCRIPT_PROMPT_TMPL.format(summaries_block=summaries_block)

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

def _inject_hook_transitions_cta(text: str, hook: str, cta: str) -> str:
    # Ensure we have a hook at the top and a CTA at the end, without doubling if model added them
    t = text.strip()
    if not t.lower().startswith(hook[:10].lower()):
        t = f"{hook}\n{t}"
    if cta.lower() not in t.lower():
        if not t.endswith((".", "!", "?")):
            t += "."
        t += f"\n{cta}"
    return t

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
    if not state.summaries or len(state.summaries) < 3:
        raise ValueError("Need at least 3 summaries to build the Instagram script.")

    preset = STYLE_PRESETS.get(style, STYLE_PRESETS["punchy"])
    hook = random.choice(HOOKS)
    cta = random.choice(CTAS)

    prompt = _compose_user_prompt(make_summaries_block(state.summaries))

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
