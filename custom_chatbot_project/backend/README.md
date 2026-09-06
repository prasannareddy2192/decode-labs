# Project 1: Custom AI Chatbot with Memory (DecodeLabs)

FastAPI + Ollama backend implementing a stateful, in-memory conversational
chat session with FIFO sliding-window pruning.

## Setup (Windows / PowerShell)

```powershell
# 1. Install Ollama if you haven't: https://ollama.com/download
ollama pull llama3

# 2. Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at `http://127.0.0.1:8000`. Docs at `http://127.0.0.1:8000/docs`.

## Quick test (no frontend needed yet)

```powershell
# Turn 1
curl -X POST http://127.0.0.1:8000/chat/demo -H "Content-Type: application/json" -d "{\"message\": \"My name is Prasanna\"}"

# Turn 2 - distract with something long
curl -X POST http://127.0.0.1:8000/chat/demo -H "Content-Type: application/json" -d "{\"message\": \"Write a short poem about the ocean\"}"

# Turn 3 - test recall (this is the brief's "System Audit: Memory Exam")
curl -X POST http://127.0.0.1:8000/chat/demo -H "Content-Type: application/json" -d "{\"message\": \"What is my name?\"}"
```

If turn 3 correctly answers "Prasanna", the memory loop works.

## Endpoints

| Method | Path                       | Purpose                          |
|--------|-----------------------------|-----------------------------------|
| POST   | `/chat/{session_id}`        | Send a message, get a reply       |
| GET    | `/chat/{session_id}/history`| View the raw stored history array |
| DELETE | `/chat/{session_id}`        | Clear a session                   |
| GET    | `/health`                   | Health check                      |

## Frontend: Stitch prompt

Paste this into Stitch (via Antigravity) to generate a matching UI:

> Design a clean, minimal chat interface for an AI chatbot called "Memory
> Chat". Layout: a scrollable message list with user messages right-aligned
> in a blue bubble and assistant messages left-aligned in a light gray
> bubble, a text input with a send button fixed at the bottom, and a small
> "New Session" button in the top-right corner that clears the conversation.
> Show a subtle turn counter (e.g. "Turn 3 / 10") near the top so the user
> can see how close they are to the sliding-window limit. Use a soft neutral
> color palette (off-white background, dark slate text), rounded corners,
> and a simple sans-serif font. No sidebar, no login screen — single-page,
> single-session chat only.

Wire the generated UI to the backend:
- Send messages to `POST http://127.0.0.1:8000/chat/{session_id}`
- Load history from `GET http://127.0.0.1:8000/chat/{session_id}/history`
- "New Session" button calls `DELETE http://127.0.0.1:8000/chat/{session_id}`

## Notes

- `MAX_TURNS` in `chat_session.py` controls the sliding window (currently 10
  turns / 20 messages). Lower it to demo the FIFO pruning behavior more
  easily.
- History is in-memory only — restarting the server clears all sessions.
  DB persistence (Postgres/Firestore) is the brief's stretch goal, not
  required for this milestone.
