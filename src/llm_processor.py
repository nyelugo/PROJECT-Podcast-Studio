"""
Podcast Studio — LLM step.
Author: Nnanyelugo Ahukannah

Turns a transcript into a structured, spoken recap. Uses OpenAI *structured
outputs* (a Pydantic schema as `response_format`) so the reply always comes back
in the exact shape we need — title, key points, and a spoken script — with no
fragile JSON parsing.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

MODEL = "gpt-4o-mini"                       # cheap + strong enough for summarising
ROOT = Path(__file__).resolve().parents[1]


class RecapScript(BaseModel):
    """The structured recap the LLM must return."""
    title: str
    key_points: list[str]
    script: str  # the spoken script that gets sent to text-to-speech


class LLMError(RuntimeError):
    """Raised for any LLM/setup problem, so the UI can show a clean message."""


def get_client() -> OpenAI:
    """Build an OpenAI client from OPENAI_API_KEY in .env (override any stale shell value)."""
    load_dotenv(ROOT / ".env", override=True)
    key = os.getenv("OPENAI_API_KEY")
    if not key or key.startswith("sk-your-key"):
        raise LLMError("No OpenAI API key found. Copy .env.example to .env and paste your key.")
    return OpenAI(api_key=key)


SYSTEM_PROMPT = (
    "You are the host of a short daily lesson-recap podcast for students. "
    "Given a class transcript, produce a warm, clear spoken recap of the key points. "
    "Structure it as: a one-line welcome, then 3-5 key takeaways explained simply, "
    "then a short encouraging sign-off. Write it to be SPOKEN ALOUD - no bullet "
    "symbols, no markdown, no headings - just flowing narration of about 150-220 words. "
    "Base it only on the transcript; do not invent facts."
)


def make_recap(client: OpenAI, document) -> RecapScript:
    """Summarise a SourceDocument into a RecapScript via structured outputs."""
    try:
        completion = client.chat.completions.parse(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",
                 "content": f"Lesson title: {document.title}\n\nTranscript:\n{document.text}"},
            ],
            response_format=RecapScript,
        )
    except Exception as exc:  # network, auth, bad request, etc.
        raise LLMError(f"LLM request failed: {exc}") from exc

    recap = completion.choices[0].message.parsed
    if recap is None or not recap.script.strip():
        raise LLMError("The model returned an empty recap. Try again with more transcript text.")
    return recap
