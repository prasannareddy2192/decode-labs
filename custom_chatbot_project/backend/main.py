"""
main.py
-------
FastAPI backend for the DecodeLabs Project 1: Custom AI Chatbot with Memory.

Flow per request (matches the brief's "Terminal Append Sequence"):
  1. Validate the incoming message (reject empty/whitespace -> avoids the
     400 Bad Request the brief warns about).
  2. Append the user's message to that session's history.
  3. Send the FULL history to Ollama as the messages payload.
  4. Append the model's reply to history.
  5. Return the reply to the client.

Run locally:
    pip install -r requirements.txt
    ollama pull llama3          # one-time, downloads the model
    uvicorn main:app --reload

Then POST to http://127.0.0.1:8000/chat/demo-session
    {"message": "My name is Prasanna"}
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import ollama

from chat_session import session_store

app = FastAPI(title="DecodeLabs Chatbot Memory - Project 1")

# Allow your frontend (Antigravity/Stitch dev server, or any localhost port)
# to call this API during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_MODEL = "llama3.2"  # swap for "qwen2.5" or any model you've pulled


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    turn_count: int


@app.post("/chat/{session_id}", response_model=ChatResponse)
def chat(session_id: str, req: ChatRequest):
    # --- Structural Validation Gate (from the brief) ---
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # 1. Append user turn
    session_store.add_message(session_id, "user", req.message.strip())

    # 2. Send full (pruned) history to the model
    history = session_store.get_history(session_id)
    try:
        response = ollama.chat(model=OLLAMA_MODEL, messages=history)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Ollama call failed - is `ollama serve` running and is "
                   f"'{OLLAMA_MODEL}' pulled? ({exc})",
        )

    reply_text = response["message"]["content"]

    # 3. Append assistant turn
    session_store.add_message(session_id, "assistant", reply_text)

    return ChatResponse(
        session_id=session_id,
        reply=reply_text,
        turn_count=len(session_store.get_history(session_id)) // 2,
    )


@app.get("/chat/{session_id}/history")
def get_history(session_id: str):
    return {"session_id": session_id, "history": session_store.get_history(session_id)}


@app.delete("/chat/{session_id}")
def reset_session(session_id: str):
    session_store.clear_session(session_id)
    return {"session_id": session_id, "status": "cleared"}


@app.get("/health")
def health():
    return {"status": "ok"}

# Serve the frontend (must be last - catches all remaining routes)
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
