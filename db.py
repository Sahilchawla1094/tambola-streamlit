"""
db.py — SQLite-backed shared game state.
All Streamlit sessions read/write the same DB file → real multiplayer.
"""
import sqlite3, json, os, threading, random, string
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "tambola.db")
_lock = threading.Lock()

# ── Schema ─────────────────────────────────────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS rooms (
    code        TEXT PRIMARY KEY,
    data        TEXT NOT NULL,        -- JSON blob for the whole room state
    updated_at  REAL DEFAULT (unixepoch('now','subsec'))
);
"""

@contextmanager
def get_conn():
    with _lock:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript(SCHEMA)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

# ── Room helpers ───────────────────────────────────────────────────────────────

def gen_code(length=6):
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    with get_conn() as c:
        for _ in range(100):
            code = "".join(random.choices(chars, k=length))
            if not c.execute("SELECT 1 FROM rooms WHERE code=?", (code,)).fetchone():
                return code
    raise RuntimeError("Failed to generate unique code")

def save_room(code: str, data: dict):
    with get_conn() as c:
        c.execute(
            "INSERT INTO rooms(code,data) VALUES(?,?) "
            "ON CONFLICT(code) DO UPDATE SET data=excluded.data, updated_at=unixepoch('now','subsec')",
            (code, json.dumps(data))
        )

def load_room(code: str) -> dict | None:
    with get_conn() as c:
        row = c.execute("SELECT data FROM rooms WHERE code=?", (code,)).fetchone()
    return json.loads(row["data"]) if row else None

def delete_room(code: str):
    with get_conn() as c:
        c.execute("DELETE FROM rooms WHERE code=?", (code,))
