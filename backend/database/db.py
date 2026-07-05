"""
Database layer — supports both:
  - Postgres (recommended for production, e.g. Neon's free tier) when
    DATABASE_URL is set
  - SQLite (zero-config local dev fallback) when it's not

Route code stays identical either way: conn.execute(sql, params) always
returns a cursor-like object with .fetchone()/.fetchall(), rows behave like
dicts, and '?' placeholders work in both (auto-converted for Postgres).
"""
import os
import uuid
import sqlite3
from datetime import datetime

DATABASE_URL = os.environ.get("DATABASE_URL", "")
SQLITE_PATH = os.path.join(os.path.dirname(__file__), "taskflow.db")

USING_POSTGRES = bool(DATABASE_URL)

if USING_POSTGRES:
    import psycopg2
    import psycopg2.extras


class _PGConnWrapper:
    """Makes a psycopg2 connection behave like the sqlite3 connection API
    the rest of the codebase already uses (conn.execute(...).fetchone())."""

    def __init__(self, real_conn):
        self._conn = real_conn

    def execute(self, sql, params=()):
        cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        pg_sql = sql.replace("?", "%s")
        cur.execute(pg_sql, params)
        return cur

    def executescript(self, script):
        cur = self._conn.cursor()
        cur.execute(script)
        return cur

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


def get_db():
    if USING_POSTGRES:
        real_conn = psycopg2.connect(DATABASE_URL)
        return _PGConnWrapper(real_conn)

    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _schema_sql():
    if USING_POSTGRES:
        return """
        CREATE TABLE IF NOT EXISTS members (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            color TEXT DEFAULT '#4F46E5',
            role TEXT DEFAULT 'member',
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            priority TEXT DEFAULT 'medium',
            due_date TEXT,
            assignee_id TEXT REFERENCES members(id) ON DELETE SET NULL,
            goal_id TEXT,
            recurrence_rule TEXT,
            recurrence_parent_id TEXT,
            google_event_id TEXT,
            created_at TEXT,
            completed_at TEXT
        );

        CREATE TABLE IF NOT EXISTS habits (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            frequency TEXT DEFAULT 'daily',
            target_per_period INTEGER DEFAULT 1,
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            assignee_id TEXT REFERENCES members(id) ON DELETE SET NULL,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS habit_logs (
            id TEXT PRIMARY KEY,
            habit_id TEXT NOT NULL REFERENCES habits(id) ON DELETE CASCADE,
            logged_date TEXT NOT NULL,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS goals (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            target_date TEXT,
            progress INTEGER DEFAULT 0,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT,
            source_type TEXT,
            embedding BYTEA,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS ai_feedback (
            id TEXT PRIMARY KEY,
            suggestion_type TEXT,
            suggestion_text TEXT,
            accepted INTEGER,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        """

    return """
    CREATE TABLE IF NOT EXISTS members (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        color TEXT DEFAULT '#4F46E5',
        role TEXT DEFAULT 'member',
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'pending',
        priority TEXT DEFAULT 'medium',
        due_date TEXT,
        assignee_id TEXT,
        goal_id TEXT,
        recurrence_rule TEXT,
        recurrence_parent_id TEXT,
        google_event_id TEXT,
        created_at TEXT,
        completed_at TEXT,
        FOREIGN KEY (assignee_id) REFERENCES members(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS habits (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        frequency TEXT DEFAULT 'daily',
        target_per_period INTEGER DEFAULT 1,
        current_streak INTEGER DEFAULT 0,
        longest_streak INTEGER DEFAULT 0,
        assignee_id TEXT,
        created_at TEXT,
        FOREIGN KEY (assignee_id) REFERENCES members(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS habit_logs (
        id TEXT PRIMARY KEY,
        habit_id TEXT NOT NULL,
        logged_date TEXT NOT NULL,
        created_at TEXT,
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS goals (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        target_date TEXT,
        progress INTEGER DEFAULT 0,
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT,
        source_type TEXT,
        embedding BLOB,
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS ai_feedback (
        id TEXT PRIMARY KEY,
        suggestion_type TEXT,
        suggestion_text TEXT,
        accepted INTEGER,
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    );
    """


def init_db(app=None):
    conn = get_db()
    conn.executescript(_schema_sql())
    conn.commit()

    existing = conn.execute("SELECT COUNT(*) as c FROM members").fetchone()["c"]
    if existing == 0:
        conn.execute(
            "INSERT INTO members (id, name, color, role, created_at) VALUES (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), "You", "#4F46E5", "admin", datetime.utcnow().isoformat()),
        )
        conn.commit()

    conn.close()
