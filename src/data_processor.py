"""
Podcast Studio — data processing step.
Author: Nnanyelugo Ahukannah

Handles the input source. MVP accepts a class transcript as pasted text or a
.txt upload, cleans it, and returns a structured `SourceDocument` that the rest
of the pipeline consumes. (Using a dataclass keeps the data standardized as it
flows between modules — one of the project's requirements.)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SourceDocument:
    """One unit of input the pipeline knows how to process."""
    title: str
    text: str
    source_type: str
    word_count: int


def _clean(text: str) -> str:
    """Normalise whitespace so the LLM sees tidy input."""
    text = text.replace("\r\n", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_transcript(text: str | None = None, file_path: str | None = None,
                    title: str = "Class Recap") -> SourceDocument:
    """Build a SourceDocument from pasted text or a .txt file.

    Raises a clear error if nothing usable was provided — the UI turns that into
    a friendly message rather than a crash.
    """
    if file_path:
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"Transcript file not found: {p}")
        text = p.read_text(encoding="utf-8")

    if not text or not text.strip():
        raise ValueError("No transcript text provided. Paste a transcript or upload a .txt file.")

    cleaned = _clean(text)
    return SourceDocument(
        title=(title or "Class Recap").strip(),
        text=cleaned,
        source_type="text",
        word_count=len(cleaned.split()),
    )


def fetch_url_text(url: str) -> str:
    """Fetch a PUBLIC web page and return its readable text.

    Great for public articles and lesson pages. It CANNOT reach pages behind a
    login (e.g. Ironhack lessons) — those just return a login page — so if we get
    back too little text, we tell the user to paste the transcript instead.
    """
    import requests
    from bs4 import BeautifulSoup

    if not url or not url.strip():
        raise ValueError("No URL provided.")
    url = url.strip()

    try:
        resp = requests.get(url, timeout=20,
                            headers={"User-Agent": "Mozilla/5.0 (PodcastStudio)"})
        resp.raise_for_status()
    except Exception as exc:
        raise ValueError(f"Couldn't fetch that URL: {exc}") from exc

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "form", "noscript"]):
        tag.decompose()
    node = soup.find("main") or soup.find("article") or soup.body or soup
    text = _clean(node.get_text("\n", strip=True))

    if len(text.split()) < 40:
        raise ValueError(
            "That page didn't return enough readable text. If it needs a login "
            "(like an Ironhack lesson), paste the transcript in the box below instead."
        )
    return text
