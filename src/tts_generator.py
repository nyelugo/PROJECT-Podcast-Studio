"""
Podcast Studio — text-to-speech step.
Author: Nnanyelugo Ahukannah

Turns the recap script into an audio file using OpenAI's TTS API. Streams the
response straight to disk so we never hold the whole audio in memory.
"""

from __future__ import annotations

from pathlib import Path

from openai import OpenAI

TTS_MODEL = "tts-1"
VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
DEFAULT_VOICE = "nova"


class TTSError(RuntimeError):
    """Raised for any text-to-speech problem, so the UI can show a clean message."""


def generate_audio(client: OpenAI, text: str, out_path: Path, voice: str = DEFAULT_VOICE) -> Path:
    """Synthesise `text` to an mp3 at `out_path` and return the path."""
    if not text or not text.strip():
        raise TTSError("Nothing to speak - the recap script is empty.")
    if voice not in VOICES:
        voice = DEFAULT_VOICE

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with client.audio.speech.with_streaming_response.create(
            model=TTS_MODEL, voice=voice, input=text
        ) as response:
            response.stream_to_file(out_path)
    except Exception as exc:
        raise TTSError(f"Text-to-speech failed: {exc}") from exc
    return out_path
