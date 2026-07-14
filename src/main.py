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
import sys
from pathlib import Path

# Let this file import its sibling modules whether run as `python src/main.py`
# or from the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from data_processor import load_transcript          # noqa: E402
from llm_processor import get_client, make_recap, LLMError, MODEL  # noqa: E402
from tts_generator import generate_audio, VOICES, DEFAULT_VOICE, TTSError  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output"


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

    def on_generate(transcript, title, voice):
        if not transcript or not transcript.strip():
            raise gr.Error("Please paste a class transcript first.")
        try:
            result = run_pipeline(transcript, title or "Class Recap", voice)
        except (LLMError, TTSError, ValueError) as exc:
            # Turn any pipeline error into a friendly toast instead of a crash.
            raise gr.Error(str(exc))
        points_md = "### Key points\n" + "\n".join(f"- {p}" for p in result["key_points"])
        return result["title"], points_md, result["script"], result["audio_path"]

    with gr.Blocks(title="Podcast Studio - Lesson Recapper") as demo:
        gr.Markdown(
            "# 🎙️ Podcast Studio — Daily Lesson Recapper\n"
            "Paste a class transcript and get a spoken recap podcast: the LLM pulls the key "
            "points, then text-to-speech reads them back to you."
        )
        with gr.Row():
            with gr.Column():
                transcript = gr.Textbox(label="Class transcript", lines=14,
                                        placeholder="Paste the transcript of your class here...")
                title = gr.Textbox(label="Lesson title (optional)",
                                   placeholder="e.g. Week 2, Day 2 — Speech Recognition")
                voice = gr.Dropdown(VOICES, value=DEFAULT_VOICE, label="Voice")
                btn = gr.Button("Generate recap podcast", variant="primary")
            with gr.Column():
                out_title = gr.Textbox(label="Episode title", interactive=False)
                out_points = gr.Markdown()
                out_script = gr.Textbox(label="Recap script", lines=8, interactive=False)
                out_audio = gr.Audio(label="Your recap podcast", type="filepath")
        btn.click(on_generate, [transcript, title, voice],
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
