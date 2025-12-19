import sqlite3
import time
import os
import logging
import uuid
from typing import List, Dict, Any, Optional
from ..config import DATA_DIR

logger = logging.getLogger("silentbot.core.db")

class DatabaseManager:
    def __init__(self, db_name: str = "silentbot.db"):
        self.db_path = os.path.join(DATA_DIR, db_name)
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._get_conn()
        c = conn.cursor()

        # Users Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                role TEXT DEFAULT 'user',
                is_pro INTEGER DEFAULT 0,
                req_count INTEGER DEFAULT 0,
                created_at REAL,
                last_active REAL
            )
        """)

        # Sessions Table (Conversations)
        c.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                title TEXT,
                created_at REAL,
                updated_at REAL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)

        # Messages Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp REAL,
                FOREIGN KEY(session_id) REFERENCES sessions(session_id)
            )
        """)
        
        # Files Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                filename TEXT,
                content BLOB,
                file_type TEXT,
                created_at REAL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)

        # Knowledge Table (Expert Modules)
        c.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT,
                content TEXT,
                expert_prompt TEXT
            )
        """)

        # Memory Table (User Facts)
        c.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                fact TEXT,
                created_at REAL,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)

        conn.commit()
        conn.close()

    # --- User Management ---
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            d = dict(row)
            d['id'] = d['user_id'] # Alias for compatibility
            return d
        return None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        conn.close()
        if row:
            d = dict(row)
            d['id'] = d['user_id']
            return d
        return None

    def create_user(self, user_id: str, username: str = "guest", role: str = "user", is_pro: bool = False):
        # If user_id is actually a username (legacy call), handle it
        if not user_id: user_id = str(uuid.uuid4())
        
        conn = self._get_conn()
        c = conn.cursor()
        now = time.time()
        try:
            c.execute("INSERT OR IGNORE INTO users (user_id, username, role, is_pro, created_at, last_active) VALUES (?, ?, ?, ?, ?, ?)",
                      (user_id, username, role, 1 if is_pro else 0, now, now))
            conn.commit()
        except Exception as e:
            logger.error(f"Error creating user: {e}")
        finally:
            conn.close()
        return self.get_user_by_id(user_id)

    def update_user_pro(self, user_id: str, is_pro: bool):
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("UPDATE users SET is_pro = ? WHERE user_id = ?", (1 if is_pro else 0, user_id))
        conn.commit()
        conn.close()

    def make_user_pro(self, user_id: str):
        self.update_user_pro(user_id, True)

    def increment_request_count(self, user_id: str):
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("UPDATE users SET req_count = req_count + 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

    # --- Session Management ---
    def create_session(self, user_id: str, title: str = "New Chat") -> str:
        session_id = str(uuid.uuid4())
        conn = self._get_conn()
        c = conn.cursor()
        now = time.time()
        c.execute("INSERT INTO sessions (session_id, user_id, title, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                  (session_id, user_id, title, now, now))
        conn.commit()
        conn.close()
        return session_id

    def list_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM sessions WHERE user_id = ? ORDER BY updated_at DESC", (user_id,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def add_message(self, session_id: str, role: str, content: str):
        conn = self._get_conn()
        c = conn.cursor()
        now = time.time()
        c.execute("INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                  (session_id, role, content, now))
        c.execute("UPDATE sessions SET updated_at = ? WHERE session_id = ?", (now, session_id))
        conn.commit()
        conn.close()

    def get_history(self, session_id: str, limit: int = 50) -> List[Dict[str, str]]:
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC LIMIT ?", (session_id, limit))
        rows = c.fetchall()
        conn.close()
        return [{"role": r["role"], "content": r["content"]} for r in rows]

    # --- Advanced Features ---
    def search_knowledge(self, query: str) -> List[Dict[str, str]]:
        # Simple keyword matching for now
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        # Find expert modules where key is in query
        c.execute("SELECT * FROM knowledge")
        rows = c.fetchall()
        conn.close()
        
        hits = []
        q_lower = query.lower()
        for r in rows:
            if r["key"].lower() in q_lower:
                hits.append(dict(r))
        return hits

    def get_memory(self, user_id: str) -> List[str]:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("SELECT fact FROM memory WHERE user_id = ? ORDER BY created_at DESC LIMIT 5", (user_id,))
        rows = c.fetchall()
        conn.close()
        return [r[0] for r in rows]

    def add_memory(self, user_id: str, fact: str):
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("INSERT INTO memory (user_id, fact, created_at) VALUES (?, ?, ?)", (user_id, fact, time.time()))
        conn.commit()
        conn.close()

# Global DB Instance
db = DatabaseManager()