"""Database initialization and schema management."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import logging
import sqlite3
from typing import Optional

from config import DB_PATH

logger = logging.getLogger(__name__)


def init_db() -> None:
    """Initialize database and create tables if they don't exist."""
    import os
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        
        # Create jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create analyses table (CV analyses) with job_id foreign key
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                name TEXT,
                email TEXT,
                phone TEXT,
                score REAL,
                jd_text TEXT,
                cv_data TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_analyses_job_id ON analyses(job_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_analyses_score ON analyses(score DESC)
        """)
        
        conn.commit()
    
    logger.info("Database initialized successfully")


def get_db_connection() -> sqlite3.Connection:
    """Get a database connection."""
    return sqlite3.connect(DB_PATH)


def get_job_by_id(job_id: int) -> Optional[dict]:
    """Get a job by ID."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_all_jobs() -> list:
    """Get all jobs."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]


def create_job(title: str, description: str) -> int:
    """Create a new job and return its ID."""
    from datetime import datetime
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO jobs (title, description, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (title, description, datetime.utcnow().isoformat(), datetime.utcnow().isoformat())
        )
        conn.commit()
        return cursor.lastrowid


def update_job(job_id: int, title: str, description: str) -> bool:
    """Update an existing job."""
    from datetime import datetime
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE jobs 
            SET title = ?, description = ?, updated_at = ?
            WHERE id = ?
            """,
            (title, description, datetime.utcnow().isoformat(), job_id)
        )
        conn.commit()
        return cursor.rowcount > 0


def delete_job(job_id: int) -> bool:
    """Delete a job and all its associated analyses."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        conn.commit()
        return cursor.rowcount > 0
