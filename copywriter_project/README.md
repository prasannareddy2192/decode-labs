# ✍️ Copy Transformer — Automated Copywriting & Tone Transformer

**Project 2 · Generative AI Internship · Decode Labs**

An AI-powered tool that generates platform-specific marketing copy from a
single product description — solving the real problem of writing distinct,
correctly-shaped content for LinkedIn, Instagram, and Email without
starting from scratch each time.

---

## 🎯 Purpose

Marketing copy isn't one-size-fits-all: a LinkedIn post, an Instagram
caption, and a marketing email all need fundamentally different structure,
length, and voice — even when promoting the exact same product. Writing
all three by hand, for every product, is repetitive and slow.

This project builds a system that takes one product description and a
desired tone, then compiles a **platform-aware prompt template** that
tells the model exactly how to shape its output differently per platform
— then exposes fine-grained control over the model's creativity via
Temperature and Top_P, so the output can range from safe/consistent to
bold/varied depending on the use case.

---

## 👥 Who This Is For

- **Small business owners / solo founders** without a marketing team, who
  need fast first-draft copy across multiple channels.
- **Marketing teams** using it as an AI-assisted first pass that a human
  then edits and polishes.
- **Freelancers/agencies** managing copy for multiple clients across
  multiple platforms.

**How it's used:** type in the product → pick the platform → pick a tone →
generate → get copy correctly shaped for that platform (paragraphs for
LinkedIn, hashtags for Instagram, subject+body for Email) → edit/publish.

---

## ⚙️ How It Performs

- Generates **structurally distinct** output per platform from the same
  input — not just reworded text, but different length, format, and
  conventions (e.g. hashtags only appear in Instagram output, a "Subject:"
  line only appears in Email output).
- **Temperature** demonstrably controls output consistency: low values
  (~0.3) produce nearly identical output across repeated runs; high values
  (~0.9) produce noticeably varied phrasing each time — verified by
  running identical prompts twice at each setting.
- **Validates input** before it reaches the model (empty product name,
  unsupported platform) with clear error messages instead of silent
  failure or a confusing model response.
- Runs **entirely locally** via Ollama — no API costs, full data privacy.

---

## 🏗️ Architecture

```
 ┌─────────────┐     POST /generate      ┌──────────────┐      build_prompt()      ┌──────────────┐
 │   Frontend   │ ───────────────────────▶ │   FastAPI    │ ───────────────────────▶ │ prompt_builder│
 │ (index.html) │                          │   backend    │                          │     .py       │
 └─────────────┘ ◀─────────────────────── └──────┬───────┘ ◀─────────────────────── └──────────────┘
                    { copy, prompt_used }         │                 compiled prompt
                                                   │
                                                   │ ollama.chat(messages, options={temperature, top_p})
                                                   ▼
                                            ┌──────────────┐
                                            │    Ollama    │
                                            │  (llama3.2)  │
                                            └──────────────┘
```

**Per-request flow:**
1. User submits `product_name`, `platform`, `tone`, `temperature`, `top_p`.
2. Backend validates: reject empty product name, reject unsupported
   platform.
3. `prompt_builder.build_prompt()` compiles the final instruction, merging
   the platform's format rules (`PLATFORM_RULES` dict) with the user's
   product/tone via an f-string template.
4. The compiled prompt is sent to Ollama along with `temperature`/`top_p`
   as generation options.
5. Generated copy is returned to the frontend (along with the exact prompt
   used, for transparency/debugging).

---

## 🛠️ Tech Stack

| Layer            | Technology                    | Why                                                  |
|--------------------|----------------------------------|---------------------------------------------------------|
| LLM                 | **Ollama** (`llama3.2`)          | Free, fully local inference — no API key/cost           |
| Backend             | **FastAPI** (Python)             | Async, typed, auto-generated API docs                   |
| Validation          | **Pydantic** (`Field` constraints)| Enforces temperature/top_p ranges automatically         |
| Prompt compilation  | Custom `prompt_builder.py`       | Isolates "what to say" logic from "how to serve it"     |
| Frontend            | HTML/CSS/JS                      | Lightweight, no build step, served directly by FastAPI  |
| Server              | **Uvicorn**                      | ASGI server for FastAPI                                  |

---

## 🚀 Setup (Windows / PowerShell)

```powershell
ollama pull llama3.2

cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open **http://127.0.0.1:8000/**. API docs at `http://127.0.0.1:8000/docs`.

---

## 🧪 Results / Testing

Tested by generating copy for the same product ("Handmade ceramic coffee
mugs") across all three platforms and two temperature settings:

| Platform  | Tone         | Temperature | Result shape                                |
|-----------|--------------|-------------|-----------------------------------------------|
| LinkedIn  | Professional | 0.3         | Structured paragraphs, credible B2B tone      |
| Instagram | Witty        | 0.9         | Short, punchy, 3-5 hashtags included          |
| Email     | Friendly     | 0.6         | "Subject:" line + short persuasive body       |

Repeating the LinkedIn (temp 0.3) test twice produced near-identical
output both times. Repeating the Instagram (temp 0.9) test twice produced
noticeably different phrasing each run — confirming Temperature genuinely
controls output variance, not just a cosmetic setting.

---

## 📡 API Endpoints

| Method | Path         | Purpose                                    |
|--------|----------------|-----------------------------------------------|
| POST   | `/generate`    | Generate copy from product/platform/tone/params |
| GET    | `/platforms`   | List supported platforms (for dynamic UI)      |
| GET    | `/health`      | Health check                                    |

---

## 📁 Project Structure

```
copywriter_project/
├── backend/
│   ├── main.py             # FastAPI app — /generate endpoint, serves frontend/
│   ├── prompt_builder.py   # Platform-aware prompt template compiler
│   └── requirements.txt
├── frontend/
│   └── index.html            # Form UI: product/platform/tone/temperature/top_p
└── README.md
```

---

## 💡 Key Design Decisions & Limitations

- **Platform rules are hardcoded in a dictionary**, not user-configurable —
  a deliberate scope choice for this milestone. A production version would
  let admins define/edit platform rules without touching code.
- **No persistence** — generated copy isn't saved anywhere; each request
  is independent (mirrors Project 1's in-memory-only scope decision).
- **Single-model** — only tested against `llama3.2`; larger models would
  likely produce more polished copy, at the cost of speed.

## 🔮 Possible Future Upgrades

- Save generation history (which pairs well with a database, as explored
  conceptually in Project 1)
- Batch-generate copy for multiple products at once
- A/B variant generation — produce 2-3 options per request to choose from
- Structured output validation (e.g. enforce Instagram's hashtag count)
  via Pydantic response models, as hinted at in the brief's stretch goals