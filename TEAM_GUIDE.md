# 👋 Team Guide — Podcast Studio (no experience needed)

New to GitHub? **You won't type a single command.** We use **GitHub Desktop** — a free app with
buttons. Everything below works the same on **Mac** and **Windows**. Take it one step at a time.

> Before you start: ask **Ugo** to add you as a collaborator on the repo (so you can access it).

---

## ✅ One-time setup (do this once, ~15 minutes)

**1. Install GitHub Desktop**
Go to **https://desktop.github.com**, download, install, and **sign in** with your GitHub account.

**2. Install Python (version 3.10 or newer)**
Go to **https://www.python.org/downloads/** and install the latest version.
👉 **Windows users:** on the first install screen, tick the box **“Add Python to PATH”**. This matters.

**3. Get your own OpenAI key**
Go to **https://platform.openai.com/api-keys**, create a key, and copy it somewhere safe.
Add a few dollars of credit (this app costs about **1 cent** per recap). *Everyone uses their own key.*

**4. Clone (download) the project — in GitHub Desktop**
`File → Clone repository → ` find **PROJECT-Podcast-Studio** → choose a folder you'll remember →
**Clone**. You now have the project on your computer.

**5. Add your key to the project**
Open the project folder. Find the file **`.env.example`**, make a **copy** of it, and rename the copy
to exactly **`.env`** (nothing before the dot). Open `.env`, and after `OPENAI_API_KEY=` paste your key.
Save. ✅ *This file stays on your computer — it is never uploaded.*

---

## ▶️ Run the app (every time you want to use it)

- **Mac:** double-click **`run.command`**. *(First time only: if Mac blocks it, right-click the file →
  Open → Open.)*
- **Windows:** double-click **`run.bat`**.

A black window opens and sets things up (the first run takes a minute). When it's ready, open
**http://localhost:7860** in your browser. **To stop:** close the black window.

---

## 🔄 Get everyone's latest changes (do this BEFORE you work)

Open **GitHub Desktop** → click **“Fetch origin”** (top). If it then shows **“Pull origin”**, click it.
That's it — you now have the newest version. **Always do this first.**

---

## 📤 Share something you changed

1. In GitHub Desktop, your changes appear in the left panel.
2. Bottom-left: type a short **Summary** of what you did (e.g. *“Add Day 3 lesson”*).
3. Click **“Commit to main”**.
4. Top: click **“Push origin”**. Done — your change is shared with the team. 🎉

---

## 🟢 Golden rules (please read)

- 🔄 **Always Pull first** (Fetch origin → Pull) before you start.
- 🙅 **Never touch `.env` or the `.venv` folder** — they're personal and already excluded.
- ✍️ **Commit small and often**, with a clear summary.
- 🖼️ **Don't drop big or personal files** (screenshots, PDFs, downloads) into the project folder.
- 🛑 **If you see a red error, the word “conflict”, or you're unsure — STOP and ask Ugo.**
  Don't click anything that says “force”. **Nothing is ever lost by asking first.**

---

## 🆘 Stuck?

Send **Ugo** a screenshot of what you see. There are genuinely no dumb questions — everyone starts here.
