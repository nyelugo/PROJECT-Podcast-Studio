# 🎙️ Podcast Studio — Daily Lesson Recapper

**Project 1 — AI Consulting Bootcamp.** An automated podcast generator: paste a class
transcript, and the app uses an LLM to pull out the key points and text-to-speech to read
them back as a short recap episode — all through a Gradio web interface.

**Author:** Nnanyelugo Ahukannah

## What it does (the pipeline)

```
Class transcript  →  LLM (structured recap)  →  Text-to-speech  →  Gradio UI
   (pasted text)       gpt-4o-mini                tts-1 (mp3)        web app
```

1. **Data processing** — clean the transcript into a structured `SourceDocument`.
2. **LLM transform** — turn it into a `RecapScript` (title, key points, spoken script) using
   OpenAI *structured outputs*, so the reply is always the exact shape we need.
3. **Text-to-speech** — synthesise the spoken script to an `.mp3`.
4. **Gradio UI** — paste transcript, pick a voice, get the recap script + audio player.

## Setup

```bash
pip install -r requirements.txt   # openai, gradio, python-dotenv, pydantic
cp .env.example .env              # then paste your OpenAI key into .env
```

`.env` is git-ignored and must never be committed.

## Running it

```bash
python src/main.py            # launch the Gradio web app (http://localhost:7860)
python src/main.py --demo     # headless: run the bundled sample transcript, save output/recap.mp3
```

> **Cost note:** each generation makes one LLM call + one TTS call — roughly a cent for a
> short transcript. Both use your OpenAI key.

## Project structure

```
PROJECT-Podcast-Studio/
├── src/
│   ├── data_processor.py   # input handling → SourceDocument (dataclass)
│   ├── llm_processor.py     # transcript → RecapScript (structured output)
│   ├── tts_generator.py     # recap script → mp3
│   └── main.py              # pipeline + Gradio app + --demo CLI
├── sample_transcript.txt    # example input for --demo
├── output/                  # generated audio lands here (mp3 git-ignored)
├── requirements.txt · .env.example · .gitignore
```

## Error handling

Every step raises a typed error (`LLMError`, `TTSError`, `ValueError`) that the UI turns into a
friendly message instead of a crash: missing API key, empty transcript, or an API failure all
show a clear toast telling you what to fix.

## Status & roadmap

**MVP (done):** text transcript → recap → audio → Gradio UI, with error handling. Verified
end-to-end (see `output/recap.mp3` from the sample transcript).

**Planned enhancements:**
- More source types: `.txt`/PDF upload, article URL.
- Richer episodes: intro/outro lines, choosable length, multiple voices.
- Nicer Gradio UX: progress feedback, download button, example gallery.
