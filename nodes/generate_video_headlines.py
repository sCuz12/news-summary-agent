# nodes/generate_instagram_headlines.py
from __future__ import annotations
from typing import List
from state import NewsAgentState
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime, timezone
import json, os, re

HEADLINE_PROMPT_TMPL = """You are writing on-screen headlines for a 60s Instagram reel.
Use the following voiceover script and the original 5 summaries to create exactly FIVE short, punchy, scannable headlines—one per story—in the SAME ORDER as the summaries.

Rules:
- 45–60 characters each (HARD limit 65), no hashtags.
- Front-load the key subject. Avoid clickbait & fluff.
- Use sentence case (not ALL CAPS).
- No ending periods.
- No emojis (we’ll add later if needed)
- Keep platform-safe wording.

Voiceover script:
---
{script_text}
---

Original summaries:
---
{summaries_block}
---

Return a JSON array of strings, order-aligned with the summaries, nothing else.
"""

load_dotenv()
client = OpenAI()  # uses OPENAI_API_KEY from env

def _summaries_block(summaries: List[str]) -> str:
    return "\n".join(f"{i+1}. {s.strip()}" for i, s in enumerate(summaries[:5]))

def _strip_code_fences(s: str) -> str:
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", s, re.IGNORECASE)
    return m.group(1).strip() if m else s.strip()

def generate_video_headlines(state: NewsAgentState) -> NewsAgentState:
    if not state.script_text:
        raise ValueError("script_text is empty. Run generate_instagram_script first.")
    if not state.summaries or len(state.summaries) < 5:
        raise ValueError("Need 5 summaries to generate headlines.")

    prompt = HEADLINE_PROMPT_TMPL.format(
        script_text=state.script_text.strip(),
        summaries_block=_summaries_block(state.summaries)
    )

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    content = resp.choices[0].message.content
    if content is None:
        raise ValueError("Error retrieving response")
    raw = content.strip()

    cleaned = _strip_code_fences(raw)
    try:
        headlines: List[str] = json.loads(cleaned)
    except Exception:
        # try to grab first JSON array
        arr = re.search(r"\[\s*\".*?\"\s*(?:,\s*\".*?\"\s*)*\]", cleaned, re.DOTALL)
        if not arr:
            raise
        headlines = json.loads(arr.group(0))

    if not isinstance(headlines, list) or len(headlines) < 3 or not all(isinstance(h, str) for h in headlines):
        raise ValueError(f"Expected 3 or more string headlines, got: {headlines}")

    # ---------- single file per run ----------
    # e.g., 2025-08-13T15-30-45Z
    run_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    out_dir = os.path.join("output", "headlines")
    os.makedirs(out_dir, exist_ok=True)

    # 1) a single TXT file with all five headlines (one file per run)
    txt_path = os.path.join(out_dir, f"headlines_{run_ts}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"Tech Brief AI — Headlines ({run_ts} UTC)\n")
        f.write("-" * 40 + "\n")
        for i, h in enumerate(headlines, 1):
            f.write(f"{i}. {h}\n")

    # 2) append to a JSONL log for history (optional but handy)
    jsonl_path = os.path.join(out_dir, "headlines_log.jsonl")
    with open(jsonl_path, "a", encoding="utf-8") as f:
        record = {
            "run_ts": run_ts,
            "headlines": headlines,
            "script_excerpt": (state.script_text or "")[:300]  # tiny context
        }
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # update state
    state.video_headlines = headlines            # List[str]

    print(f"📰 Headlines saved to {txt_path} (and appended to {jsonl_path}).")
    return state
