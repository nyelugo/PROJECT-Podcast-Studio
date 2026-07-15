# Project 1 Presentation — Podcast Studio (Content Recapper)

**Team:** Adam · Ugo · Anand
**Slot:** ~10 minutes total → **~7 min presenting + ~3 min Q&A**
**Structure (from the brief):** Introduction → Problem → Demo → Takeaways

> This is our alignment script. Once we're happy with it, it becomes the slide deck.

---

## Running order & timing

| # | Who | Part | Time |
|---|---|---|---|
| 1 | **Adam** | Introduction + Problem | ~2:00 |
| 2 | **Ugo** | Live Demo | ~3:30 |
| 3 | **Anand** | Takeaways + Technical choices + What's next | ~1:30 |
| 4 | **All 3** | Q&A | ~3:00 |

**Total: ~7 min presenting (2:00 + 3:30 + 1:30) + ~3 min Q&A ≈ 10 min.**

Demo is the star — biggest slice. Intro/Problem set it up fast; Anand lands the "why" and the future.

---

## How it works — the pipeline  (→ becomes the "How it works" slide)

```
INPUT  ─▶  LLM  ─▶  TEXT-TO-SPEECH  ─▶  GRADIO APP
```

1. **Input** — pick a saved lesson, a public URL, or an uploaded file (.txt/.md/.pdf)  ·  `data_processor`
2. **LLM** — `gpt-4o-mini` returns a **structured** recap: title, key points, spoken script  ·  `llm_processor` (Pydantic)
3. **Text-to-speech** — `tts-1` turns the script into an **mp3**  ·  `tts_generator`
4. **Gradio app** — play and read the recap  ·  `main.py`

One clean pipeline, four swappable modules. *(The deck will render this as four boxes with arrows.)*

## Technical highlights (pick 2–3 to say live; the rest are Q&A cribs)

**Say live (strongest):**
- **Structured outputs (Pydantic schema):** the LLM must return title + key points + script in an exact shape — no hallucinated or broken formatting.
- **Deliberate model choices:** `gpt-4o-mini` (cheap, fast, strong at summarising) for text + `tts-1` for natural voice → **~1¢ per recap**.
- **Appropriate data structures:** a `dataclass` for the input document and a Pydantic model for the recap — clean, typed data between modules.

**Q&A cribs (only if asked):**
- **Prompt design:** system prompt asks for a *spoken* script, grounded in the source text, fixed length.
- **Modular + error handling:** separate data / LLM / TTS / UI steps; typed errors become friendly UI messages, not crashes.
- **Auto-discovering picker:** the dropdown builds itself from the files in `input/` — drop in a lesson, it shows up.
- **Simple by design:** OpenAI TTS streams mp3 straight to disk (no ffmpeg); API key lives in a git-ignored `.env`.
- **Team-ready:** cross-platform double-click launchers + venv with a Python-version check (README + TEAM_GUIDE).

---

## 1. Adam — Introduction + Problem (~2 min)

**Introduction (~2:00)**
- "Hi, we're **Adam, Ugo, and Anand**. We built **Podcast Studio — a Content Recapper**."
- Each day at IronHack we cover multiple lessons on different, and dense, topics. It is difficult to remember all of the topics and how they relate to each other.
- It takes a lot of time to catch up with the material and to ensure it sticks.
- We thought, why not organize, summarize, and listen to the notes instead!
- We created a workflow that takes each day's lessons, organizes the content, and presents it in one easy to use daily lesson recap.
- Since you don't have a lot of time given the full on Bootcamp workload, we also ensured that each daily lesson is only 1 minute. You can listen to it on the way to class or in the few mins every morning it takes for everyone to arrive.
- We hope this makes your experience at IronHack more manageable!
- Ugo will now show you how it works.

---

## 2. Ugo — Live Demo (~3:30)  ⭐ the main event

**Before you start:** app already open at `http://localhost:7860`, Wi-Fi checked, a backup `.mp3` ready.

**Click path (rehearse this until it's muscle memory):**
1. "This is the app. On the left I **pick a saved lesson** — let's do one we all just took: *Week 2 · Day 1 · Speech Recognition*."
2. Click **Generate recap podcast**.
3. As it runs, narrate **one or two technical choices** *(this is graded)*:
   - "The lesson text goes to an **LLM that returns a structured result** — title, key points, and a spoken script — using a **schema**, so the output is always the right shape and can't drift into broken formatting."
   - "Then **OpenAI text-to-speech** reads that script back as audio."
4. Show the three outputs: **Episode title → Key points → Recap script**.
5. **Play the audio.** Let a few seconds of it actually play — that's the wow moment.
6. Quick flexibility mention (~10s, keep it verbal — stay on the reliable saved-lesson path, no live fetch): "It also takes a **public URL** or an **uploaded file** (.txt, .md, .pdf), so it works for lessons, articles, or your own notes too."
7. Hand off: *"Anand will cover what we learned and where we'd take it."*

**If the live run stalls (Wi-Fi/API):** immediately **play a pre-generated `.mp3` from `output/`** and keep narrating. Never stare at a spinner.

> Note: keep the demo on **pick-a-saved-lesson** — it's fast and reliable. We're not featuring the login-only-pages caveat; no need to raise it.

---

## 3. Anand — Takeaways + Technical choices + What's next (~1:30)

**What we learned**
- "**Prompt design matters** — asking for a *spoken* script (natural sentences, no bullets) beats a bullet summary."
- "**Flexible inputs** — pick a saved lesson, fetch a public URL, or upload a file, so it works for lessons, articles, or your own notes."

**Technical choices (say these — they're graded; the "How it works" diagram slide backs this up)**
- **Structured outputs (Pydantic):** the LLM returns title + key points + script in a fixed shape — reliable, no broken formatting.
- **Deliberate model choices:** `gpt-4o-mini` + `tts-1` → strong results at **~1¢ per recap**.
- **Modular + robust:** separate data / LLM / TTS / UI modules, each testable, with typed error handling (friendly messages, not crashes).

**What's next**
- Download button · PDF input · intro/outro music · choose-the-length · **deploy online** (e.g. Hugging Face Spaces) so anyone can use it.
- Closing line: *"Thanks — happy to take questions."*

---

## 4. Q&A (~3 min) — split domains so nobody freezes

| Question type | Who answers | Crisp answer |
|---|---|---|
| "Who would actually use this?" | **Adam** | Students reviewing on the go; accessibility; onboarding/training recaps. |
| "Could your team run it?" | **Adam** | Yes — README + TEAM_GUIDE + double-click launchers, Mac & Windows. |
| Demo / product ("can it do X?") | **Ugo** | Show or describe; scope is one lesson → one recap, extensible. |
| Cost | **Ugo** | ~**1 cent** per recap (one LLM call + one TTS call). |
| "How do you stop it making things up?" | **Anand** | Structured output + the prompt **grounds it in the provided text**. |
| "Why OpenAI for both?" | **Anand** | One key/bill, strong integration, TTS returns mp3 (no extra tools). |

---

## Logistics / de-risk checklist (before we present)

- [ ] App running at `localhost:7860`, tested once end-to-end today.
- [ ] A backup recap `.mp3` open and ready to play.
- [ ] Everyone knows their part and the **handoff lines**.
- [ ] One dry run, timed, to confirm we land under 7 minutes.
- [ ] Repo is pushed and clean (README, TEAM_GUIDE, example audio all present).

---

## Notes / edits (add anything here as we align)

-
