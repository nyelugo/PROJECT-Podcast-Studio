"""
Podcast Studio — Content Recapper.
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

from data_processor import load_transcript, fetch_url_text, read_local_file   # noqa: E402
from llm_processor import get_client, make_recap, LLMError, MODEL  # noqa: E402
from tts_generator import generate_audio, VOICES, DEFAULT_VOICE, TTSError  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output"
INPUT_DIR = ROOT / "input"

# The three input sources (radio) — exactly one is used per generation.
SRC_LESSON, SRC_URL, SRC_FILE = "Saved lesson", "Public URL", "Upload a file"

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

    def on_generate(source_type, lesson, url, file_path, voice):
        try:
            # Exactly one source, chosen by the radio. The title is derived
            # automatically; the model also names the episode.
            if source_type == SRC_LESSON:
                if not lesson:
                    raise gr.Error("Please pick a saved lesson from the dropdown.")
                source_text = Path(lesson).read_text(encoding="utf-8")
                title = dict((v, k) for k, v in list_saved_lessons()).get(lesson, "Lesson Recap")
            elif source_type == SRC_URL:
                if not (url and url.strip()):
                    raise gr.Error("Please paste a public (non-login) URL.")
                source_text = fetch_url_text(url)
                title = "Lesson Recap"
            else:  # SRC_FILE
                if not file_path:
                    raise gr.Error("Please upload a .txt, .md, or .pdf file.")
                source_text = read_local_file(file_path)
                title = "Lesson Recap"
            result = run_pipeline(source_text, title, voice)
        except (LLMError, TTSError, ValueError) as exc:
            # Turn any pipeline error into a friendly toast instead of a crash.
            raise gr.Error(str(exc))
        points_md = "### Key points\n" + "\n".join(f"- {p}" for p in result["key_points"])
        return result["title"], points_md, result["script"], result["audio_path"]

    with gr.Blocks(title="Podcast Studio - Content Recapper") as demo:
        gr.Markdown(
            "# 🎙️ Podcast Studio — Content Recapper\n"
            "**Turn any lesson, article, or report into a short spoken recap.** Pick **one** source "
            "below, then hit **Generate** — an LLM pulls the key points and text-to-speech reads "
            "them back.\n\n"
            "*Public URLs only — password-protected pages (e.g. Ironhack lessons) can't be fetched; "
            "upload those as a file instead.*"
        )
        with gr.Row():
            with gr.Column():
                # One radio picks the source; only the matching input is shown.
                source_type = gr.Radio([SRC_LESSON, SRC_URL, SRC_FILE], value=SRC_LESSON,
                                       label="Where's the lesson from?")
                lesson = gr.Dropdown(choices=list_saved_lessons(), value=None,
                                     label="📚 Pick a saved lesson",
                                     info="Files in the input/ folder.", visible=True)
                url = gr.Textbox(label="🔗 Public lesson / article URL",
                                 placeholder="https://… a public (non-login) page", visible=False)
                file_in = gr.File(label="📄 Upload a file (.txt, .md, .pdf)",
                                  file_types=[".txt", ".md", ".markdown", ".pdf"],
                                  type="filepath", visible=False)
                voice = gr.Dropdown(VOICES, value=DEFAULT_VOICE, label="Voice")
                btn = gr.Button("Generate recap podcast", variant="primary")
            with gr.Column():
                # Order: title, then the audio (the deliverable), then the supporting text.
                out_title = gr.Textbox(label="Episode title", interactive=False)
                out_audio = gr.Audio(label="Your recap podcast", type="filepath")
                out_points = gr.Markdown()
                # The full script is long, so keep it tucked away and expandable.
                with gr.Accordion("Recap script", open=False):
                    out_script = gr.Textbox(label="Recap script", lines=8,
                                            interactive=False, show_label=False)

        def _show_source(choice):
            """Show only the input that matches the selected source."""
            return (gr.update(visible=choice == SRC_LESSON),
                    gr.update(visible=choice == SRC_URL),
                    gr.update(visible=choice == SRC_FILE))

        source_type.change(_show_source, source_type, [lesson, url, file_in])

        btn.click(on_generate, [source_type, lesson, url, file_in, voice],
                  [out_title, out_points, out_script, out_audio])
    return demo


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Podcast Studio — Content Recapper")
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
