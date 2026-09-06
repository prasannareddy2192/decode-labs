"""
chat_session.py
----------------
Holds the in-memory conversation history for each chat session.

Core ideas from the project brief:
- H_(t-1): the historical array of all messages up to now, stored per session_id.
- Every turn appends the user's message, then (after the model responds) the
  model's reply, so the array always reflects the full back-and-forth.
- FIFO sliding window: once a session's history grows past MAX_TURNS, we drop
  the oldest user/assistant pair so the payload sent to the model doesn't
  grow forever and blow the context window / token budget.
"""

from typing import Dict, List, TypedDict


class Message(TypedDict):
    role: str      # "user" or "assistant"
    content: str


# Each "turn" = 1 user message + 1 assistant reply = 2 entries in the list.
# MAX_TURNS=10 -> at most 20 messages kept per session.
MAX_TURNS = 10
MAX_MESSAGES = MAX_TURNS * 2


class ChatSessionStore:
    """
    Simple in-memory store: { session_id: [ {role, content}, ... ] }

    NOTE: This lives in RAM (as the brief's own slides call out under
    "The Ephemeral Nature of Local RAM") - if the server restarts, all
    sessions are lost. That's fine for this milestone; the brief's
    Postgres/Firestore section is the future upgrade path, not required here.
    """

    def __init__(self) -> None:
        self._sessions: Dict[str, List[Message]] = {}

    def _ensure_session(self, session_id: str) -> None:
        if session_id not in self._sessions:
            self._sessions[session_id] = []

    def get_history(self, session_id: str) -> List[Message]:
        self._ensure_session(session_id)
        return self._sessions[session_id]

    def add_message(self, session_id: str, role: str, content: str) -> None:
        self._ensure_session(session_id)
        self._sessions[session_id].append({"role": role, "content": content})
        self._prune(session_id)

    def _prune(self, session_id: str) -> None:
        """FIFO trim: drop oldest messages once we exceed MAX_MESSAGES."""
        history = self._sessions[session_id]
        if len(history) > MAX_MESSAGES:
            overflow = len(history) - MAX_MESSAGES
            self._sessions[session_id] = history[overflow:]

    def clear_session(self, session_id: str) -> None:
        self._sessions[session_id] = []

    def session_exists(self, session_id: str) -> bool:
        return session_id in self._sessions


# Single shared instance used by the FastAPI app (acts like a module-level
# "database" for the lifetime of the running server process).
session_store = ChatSessionStore()
