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
