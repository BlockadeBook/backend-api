import os
import psycopg2
from psycopg2.extras import RealDictCursor

_conn = None


def get_connection():
    global _conn
    if _conn is None or _conn.closed:
        _conn = psycopg2.connect(
            host=os.getenv("ADMIN_DB_HOST", "localhost"),
            port=int(os.getenv("ADMIN_DB_PORT", 5432)),
            dbname=os.getenv("ADMIN_DB_NAME", "admin"),
            user=os.getenv("ADMIN_DB_USER", "admin"),
            password=os.getenv("ADMIN_DB_PASSWORD", "admin"),
        )
        _conn.autocommit = True
    return _conn


def get_cursor():
    return get_connection().cursor(cursor_factory=RealDictCursor)


def init_db():
    with get_cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(150) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
