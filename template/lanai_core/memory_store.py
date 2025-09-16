# memory_store.py — SQLite-first (stdlib), Postgres optionnel via import dynamique
import os, sqlite3, contextlib
from typing import List, Dict, Optional
from urllib.parse import urlparse

# Config: par défaut SQLite local ./data/app.db ; supporte DATABASE_URL/DB_URL
def _db_url() -> str:
    return os.getenv("DATABASE_URL") or os.getenv("DB_URL") or "sqlite:///./data/app.db"

def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite:")

def _sqlite_path(url: str) -> str:
    # sqlite:///C:/path/db.sqlite  ou  sqlite:///./data/app.db
    path = url.split("sqlite:///", 1)[1] if "sqlite:///" in url else url.split("sqlite:", 1)[1]
    return path

def _ensure_parent_dir(p: str) -> None:
    d = os.path.dirname(os.path.abspath(p))
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def _get_conn():
    url = _db_url()
    if _is_sqlite(url):
        path = _sqlite_path(url)
        _ensure_parent_dir(path)
        conn = sqlite3.connect(path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    # Postgres optionnel (seulement si psycopg2 dispo)
    try:
        import psycopg2
        parsed = urlparse(url)
        conn = psycopg2.connect(url)
        return conn
    except Exception as e:
        raise RuntimeError("DATABASE_URL non-sqlite et psycopg2 indisponible. "
                           "Installez psycopg2 OU passez à sqlite:///…") from e

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  direction TEXT NOT NULL CHECK (direction IN ('IN','OUT')),
  text TEXT NOT NULL,
  message_sid TEXT UNIQUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_messages_user_created ON messages(user_id, created_at);
"""

def init_schema() -> None:
    with contextlib.closing(_get_conn()) as conn:
        cur = conn.cursor()
        if isinstance(conn, sqlite3.Connection):
            cur.executescript(SCHEMA_SQL)
        else:
            # Postgres: adapter en multi-statements
            for stmt in [s for s in SCHEMA_SQL.split(";") if s.strip()]:
                cur.execute(stmt + ";")
        conn.commit()

def add_message(user_id: str, direction: str, text: str, message_sid: Optional[str] = None) -> bool:
    """
    Ajoute un message. Si message_sid est fourni et déjà vu, ignore (idempotence).
    Retourne True si inséré, False si ignoré.
    """
    with contextlib.closing(_get_conn()) as conn:
        cur = conn.cursor()
        if isinstance(conn, sqlite3.Connection):
            cur.execute(
                "INSERT OR IGNORE INTO messages(user_id, direction, text, message_sid) VALUES(?,?,?,?)",
                (user_id, direction, text, message_sid),
            )
        else:
            cur.execute(
                "INSERT INTO messages(user_id, direction, text, message_sid) VALUES(%s,%s,%s,%s) ON CONFLICT (message_sid) DO NOTHING",
                (user_id, direction, text, message_sid),
            )
        conn.commit()
        return cur.rowcount > 0

def has_seen(message_sid: str) -> bool:
    if not message_sid:
        return False
    with contextlib.closing(_get_conn()) as conn:
        cur = conn.cursor()
        if isinstance(conn, sqlite3.Connection):
            cur.execute("SELECT 1 FROM messages WHERE message_sid=? LIMIT 1", (message_sid,))
        else:
            cur.execute("SELECT 1 FROM messages WHERE message_sid=%s LIMIT 1", (message_sid,))
        return cur.fetchone() is not None

def get_history(user_id: str, limit: int = 8) -> List[Dict]:
    """
    Renvoie les derniers messages (IN/OUT, text) pour l’utilisateur.
    Ordre chronologique (anciens -> récents) pour prompt LLM.
    """
    with contextlib.closing(_get_conn()) as conn:
        cur = conn.cursor()
        if isinstance(conn, sqlite3.Connection):
            cur.execute(
                "SELECT direction, text FROM messages WHERE user_id=? ORDER BY id DESC LIMIT ?",
                (user_id, limit),
            )
        else:
            cur.execute(
                "SELECT direction, text FROM messages WHERE user_id=%s ORDER BY id DESC LIMIT %s",
                (user_id, limit),
            )
        rows = cur.fetchall()
        # on inverse pour donner (anciens -> récents)
        return [{"direction": r[0], "text": r[1]} for r in rows[::-1]]
