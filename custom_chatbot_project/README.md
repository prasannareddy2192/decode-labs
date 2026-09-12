# 🧠 Memory Chat — Custom AI Chatbot with Memory

**Project 1 · Generative AI Internship · Decode Labs**

A locally-hosted AI chatbot that solves one of the most fundamental problems
in LLM application development: **large language models are stateless.**
Every single API call starts with zero memory of anything that came before
it. This project engineers "memory" on top of a stateless model using
session-state management, giving the chatbot the ability to hold a coherent,
context-aware conversation across many turns.

---

## 🎯 Purpose

The goal of this project was to move beyond "just calling an LLM API" and
understand the actual mechanics that power every conversational AI product
you've ever used — ChatGPT, Claude, Gemini, all of it. None of these models
inherently remember you. What feels like memory is a carefully engineered
illusion: the entire conversation transcript is resent to the model on every
turn, so it can "read" the past even though it never truly stored it.

This project builds that illusion from scratch — no memory frameworks, no
managed session APIs, just the raw mechanics: an in-memory history array,
structured message objects, and a sliding-window strategy to keep the
system stable as conversations grow.

---

## ⚙️ How It Performs

- Holds a coherent conversation across **multiple turns**, correctly
  recalling facts (names, preferences, prior answers) stated earlier in the
  session — even after being "distracted" by unrelated questions in
  between.
- Automatically **prunes old messages** once a session exceeds 10 exchanges
  (20 messages), preventing unbounded growth of the payload sent to the
  model and avoiding context-window overflow.
- **Validates input** before it reaches the model — empty or whitespace-only
  messages are rejected with a clear error instead of silently failing.
- **Isolates sessions** — each `session_id` has its own independent history,
  so multiple conversations never bleed into each other.
- Runs **entirely locally** via Ollama — no API keys, no per-token costs,
  full data privacy.

---

## 🏗️ Architecture & Flow

```
 ┌─────────────┐        POST /chat/{session_id}        ┌──────────────┐
 │   Frontend   │ ─────────────────────────────────────▶ │   FastAPI    │
 │ (index.html) │                                        │   backend    │
 └─────────────┘ ◀───────────────────────────────────── └──────┬───────┘
                         { reply, turn_count }                  │
                                                                 │ 1. validate input
                                                                 │ 2. append user msg
                                                                 │ 3. send FULL history
                                                                 ▼
                                                          ┌──────────────┐
                                                          │    Ollama    │
                                                          │  (llama3.2)  │
                                                          └──────┬───────┘
                                                                 │ 4. model reply
                                                                 ▼
                                                     append reply to history
                                                     (prune if > 20 messages)
```

**Per-request flow:**
1. User sends a message → validated (reject empty/whitespace).
2. Message appended to that session's in-memory history list as
   `{"role": "user", "content": "..."}`.
3. The **entire** history (not just the new message) is sent to Ollama.
4. The model's reply is appended to history as `{"role": "assistant", ...}`.
5. If the session now exceeds `MAX_MESSAGES` (20), the oldest entries are
   dropped (FIFO) to keep the payload bounded.
6. Reply returned to the frontend and rendered in the chat UI.

---

## 🛠️ Tech Stack

| Layer          | Technology                          | Why                                                |
|-----------------|---------------------------------------|-----------------------------------------------------|
| LLM              | **Ollama** (`llama3.2`)               | Free, fully local inference — no API key/cost       |
| Backend          | **FastAPI** (Python)                  | Async, typed, auto-generated API docs               |
| Validation       | **Pydantic**                          | Request/response schema enforcement                 |
| Session storage  | In-memory Python dict (custom)        | Sufficient for this milestone; DB is a future step  |
| Frontend         | Vanilla **HTML/CSS/JS**               | Lightweight, no build step, single file, served directly by FastAPI |
| Server           | **Uvicorn**                           | ASGI server for FastAPI                              |

---

## 🚀 Setup (Windows / PowerShell)

```powershell
# 1. Install Ollama: https://ollama.com/download
ollama pull llama3.2

# 2. Set up the backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open **http://127.0.0.1:8000/** — the chat UI is served directly from the
FastAPI backend (single port, single link). Interactive API docs are
available at `http://127.0.0.1:8000/docs`.

---

## 🧪 Testing the Memory Loop

Try this sequence in the UI to see the memory system in action:

1. `My name is Prasanna and my favorite language is Python`
2. `Write a 4-line poem about the ocean` *(distraction)*
3. `What's my name and favorite language?` *(recall test)*

Step 3 should correctly answer both facts — proving the history array is
round-tripping correctly through frontend → backend → model → back.

**Testing the API directly (PowerShell):** note that `curl` in PowerShell is
aliased to `Invoke-WebRequest`, which doesn't accept `-H`/`-d` the way real
curl does — use `Invoke-RestMethod` instead:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/chat/demo -Method Post -ContentType "application/json" -Body '{"message": "My name is Prasanna"}'
```

---

## 📡 API Endpoints

| Method | Path                          | Purpose                            |
|--------|---------------------------------|--------------------------------------|
| POST   | `/chat/{session_id}`           | Send a message, get a reply          |
| GET    | `/chat/{session_id}/history`   | View the raw stored history array    |
| DELETE | `/chat/{session_id}`           | Clear a session                      |
| GET    | `/health`                      | Health check                         |

---

## 📁 Project Structure

```
chatbot-memory/
├── backend/
│   ├── main.py            # FastAPI app — chat endpoint, serves frontend/
│   ├── chat_session.py    # In-memory session store + FIFO sliding window
│   └── requirements.txt
├── frontend/
│   └── index.html          # Chat UI
└── README.md
```

---

## 🩹 Troubleshooting

- **`uvicorn: command not found`** — your virtual environment isn't active
  in the current terminal. Run `cd backend` then `venv\Scripts\activate`
  and confirm `(venv)` appears before the prompt.
- **`ollama call failed`** — make sure Ollama is running and the model in
  `OLLAMA_MODEL` (in `main.py`) has actually been pulled. Check with
  `ollama list`.
- **PowerShell `curl` errors about `-Headers`** — see the
  `Invoke-RestMethod` note above; PowerShell's built-in `curl` alias isn't
  real curl.

---

## 💡 Key Design Decisions & Limitations

- **In-memory only, by design.** History lives in RAM and is lost on
  server restart. This matches the brief's scope for this milestone —
  persistent storage (Postgres/Firestore) is explicitly framed as a later,
  more advanced upgrade, not a Project 1 requirement.
- **FIFO sliding window over token-based trimming.** Pruning is based on
  message *count* (`MAX_TURNS = 10`), not actual token count — a simpler
  but effective approximation for this scale.
- **Memory ≠ factual accuracy.** The system reliably recalls what was said
  earlier in a conversation, but the underlying model (`llama3.2`, a small
  local model) can still be factually wrong about general knowledge. These
  are two separate concerns — this project solves the first.

---

## 🔮 Possible Future Upgrades

- Swap in-memory storage for Postgres/SQLite so sessions survive restarts
- Token-based (not message-count-based) sliding window using a tokenizer
- Multi-user auth so sessions map to real user accounts
- Streaming responses instead of waiting for the full reply

---

## 👤 Author

**Sai Prasanna Gedela**
Generative AI Intern @ Decode Labs
GitHub: [prasannareddy2192](https://github.com/prasannareddy2192)