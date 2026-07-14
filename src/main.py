"""
Podcast Studio — Daily Lesson Recapper.
Author: Nnanyelugo Ahukannah

End-to-end pipeline:  transcript  ->  LLM recap  ->  text-to-speech  ->  Gradio UI.

Usage:
    python src/main.py            # launch the Gradio web app
    python src/main.py --demo     # headless: run the bundled sample transcript, save audio
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Let this file import its sibling modules whether run as `python src/main.py`
# or from the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from data_processor import load_transcript, fetch_url_text   # noqa: E402
from llm_processor import get_client, make_recap, LLMError, MODEL  # noqa: E402
from tts_generator import generate_audio, VOICES, DEFAULT_VOICE, TTSError  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output"
INPUT_DIR = ROOT / "input"

# Acronyms we want to keep upper-cased when prettifying file/folder names.
_ACRONYMS = {"Ai": "AI", "Ml": "ML", "Llm": "LLM", "Llms": "LLMs", "Json": "JSON",
             "Stt": "STT", "Nn": "NN", "Api": "API", "Ui": "UI"}


def _pretty(token: str) -> str:
    """'week1' -> 'Week 1', 'ai-literacy' -> 'AI Literacy'."""
    token = re.sub(r"(?<=[A-Za-z])(?=\d)", " ", token).replace("-", " ").replace("_", " ")
    return " ".join(_ACRONYMS.get(w.capitalize(), w.capitalize()) for w in token.split())


def list_saved_lessons() -> list[tuple[str, str]]:
    """Every .txt under input/, as (nice label, filepath) for the dropdown."""
    if not INPUT_DIR.exists():
        return []
    items = []
    for p in sorted(INPUT_DIR.rglob("*.txt")):
        crumbs = [_pretty(x) for x in p.relative_to(INPUT_DIR).parts[:-1]] + [_pretty(p.stem)]
        items.append((" · ".join(crumbs), str(p)))
    return items


def run_pipeline(transcript: str, title: str, voice: str) -> dict:
    """Run the whole pipeline and return a result dict. Raises on any step failing."""
    document = load_transcript(text=transcript, title=title)
    client = get_client()
    recap = make_recap(client, document)
    audio_path = generate_audio(client, recap.script, OUTPUT_DIR / "recap.mp3", voice=voice)
    return {
        "title": recap.title,
        "key_points": recap.key_points,
        "script": recap.script,
        "audio_path": str(audio_path),
        "source_words": document.word_count,
    }


# --------------------------------------------------------------------------
# Gradio web interface
# --------------------------------------------------------------------------

def build_ui():
    import gradio as gr

    def on_generate(lesson, url, transcript, voice):
        if not lesson and not (url and url.strip()) and not (transcript and transcript.strip()):
            raise gr.Error("Pick a saved lesson, paste a URL, or paste a transcript.")
        try:
            # Priority: a picked saved lesson, then a URL, then pasted text
            # (pasting is needed for login-only pages like Ironhack lessons).
            # The title is derived automatically; the model also names the episode.
            if lesson:
                source_text = Path(lesson).read_text(encoding="utf-8")
                title = dict((v, k) for k, v in list_saved_lessons()).get(lesson, "Lesson Recap")
            elif url and url.strip():
                source_text = fetch_url_text(url)
                title = "Lesson Recap"
            else:
                source_text = transcript
                title = "Lesson Recap"
            result = run_pipeline(source_text, title, voice)
        except (LLMError, TTSError, ValueError) as exc:
            # Turn any pipeline error into a friendly toast instead of a crash.
            raise gr.Error(str(exc))
        points_md = "### Key points\n" + "\n".join(f"- {p}" for p in result["key_points"])
        return result["title"], points_md, result["script"], result["audio_path"]

    with gr.Blocks(title="Podcast Studio - Lesson Recapper") as demo:
        gr.Markdown(
            "# 🎙️ Podcast Studio — Daily Lesson Recapper\n"
            "**Pick a saved lesson** from the list and hit **Generate** — an LLM pulls the key points, "
            "then text-to-speech reads them back as a short recap.\n\n"
            "*Recapping something else? Use the URL / transcript panel below. Login-only pages "
            "(e.g. Ironhack lessons) can't be fetched by URL — save or paste their text instead.*"
        )
        with gr.Row():
            with gr.Column():
                lesson = gr.Dropdown(choices=list_saved_lessons(), value=None,
                                     label="📚 Pick a saved lesson",
                                     info="Files in the input/ folder — select one and hit Generate.")
                with gr.Accordion("… or use a URL / paste a transcript", open=False):
                    url = gr.Textbox(label="Lesson URL (public pages)",
                                     placeholder="https://… a public article or lesson page")
                    transcript = gr.Textbox(label="… or paste the transcript", lines=8,
                                            placeholder="Paste the lesson/class transcript here...")
                voice = gr.Dropdown(VOICES, value=DEFAULT_VOICE, label="Voice")
                btn = gr.Button("Generate recap podcast", variant="primary")
            with gr.Column():
                out_title = gr.Textbox(label="Episode title", interactive=False)
                out_points = gr.Markdown()
                out_script = gr.Textbox(label="Recap script", lines=8, interactive=False)
                out_audio = gr.Audio(label="Your recap podcast", type="filepath")
        btn.click(on_generate, [lesson, url, transcript, voice],
                  [out_title, out_points, out_script, out_audio])
    return demo


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Podcast Studio — Daily Lesson Recapper")
    parser.add_argument("--demo", action="store_true",
                        help="Headless run on the bundled sample transcript (no web UI).")
    args = parser.parse_args()

    if args.demo:
        sample = ROOT / "sample_transcript.txt"
        text = sample.read_text(encoding="utf-8") if sample.exists() else ""
        print(f"Running pipeline (model={MODEL}) on the sample transcript...\n")
        result = run_pipeline(text, "Week 2, Day 2 — Speech Recognition", DEFAULT_VOICE)
        print("Episode title:", result["title"])
        print("\nKey points:")
        for p in result["key_points"]:
            print("  -", p)
        print("\nScript:\n", result["script"])
        print("\nAudio saved to:", result["audio_path"])
    else:
        build_ui().launch()


if __name__ == "__main__":
    main()
