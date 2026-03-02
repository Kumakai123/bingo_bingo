"""
One-time migration: add session_id column to simulated_bets table.

Run once on the deployed server:
    cd /path/to/backend
    python -m scripts.migrate_add_session_id

Existing rows get session_id = 'legacy' so they don't break NOT NULL constraint.
"""
import sqlite3
import sys
from pathlib import Path

# Resolve DB path relative to project root
DB_PATH = Path(__file__).resolve().parent.parent / "bingo.db"


def migrate():
    if not DB_PATH.exists():
        print(f"DB not found at {DB_PATH}, skipping migration.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Check if column already exists
    cursor.execute("PRAGMA table_info(simulated_bets)")
    columns = [row[1] for row in cursor.fetchall()]

    if "session_id" in columns:
        print("session_id column already exists, skipping.")
        conn.close()
        return

    print("Adding session_id column to simulated_bets...")
    cursor.execute(
        "ALTER TABLE simulated_bets ADD COLUMN session_id VARCHAR(36) DEFAULT 'legacy' NOT NULL"
    )
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_simulated_bets_session_id ON simulated_bets(session_id)")
    conn.commit()
    conn.close()
    print("Done.")


if __name__ == "__main__":
    migrate()
