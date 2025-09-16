# core.py — noyau générique (LIB), sans Flask/Twilio/OpenAI
import os
from typing import Callable, List, Dict
from memory_store import init_schema, add_message, has_seen, get_history

def bootstrap_memory() -> None:
    os.environ.setdefault("DATABASE_URL", "sqlite:///./data/app.db")
    init_schema()

def process_incoming(user_id: str,
                     text_in: str,
                     message_sid: str | None,
                     generate_fn: Callable[[str, List[Dict]], str]) -> str | None:
    """
    - Idempotence via message_sid (si déjà vu -> None)
    - Mémoire courte (8 tours) envoyée à generate_fn
    - Log IN puis OUT
    """
    if message_sid and has_seen(message_sid):
        return None
    text_in = (text_in or "").strip() or "Salut"
    add_message(user_id, "IN", text_in, message_sid)
    history = get_history(user_id, limit=8)
    reply_text = (generate_fn(text_in, history) or "").strip() or "D'accord."
    add_message(user_id, "OUT", reply_text, None)
    return reply_text
