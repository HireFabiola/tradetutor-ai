import sqlite3
from pathlib import Path
from datetime import datetime


DB_PATH = Path("data/tradetutor.db")


def initialize_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS learner_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_id TEXT NOT NULL,
                numeric_answer REAL NOT NULL,
                is_correct INTEGER NOT NULL,
                reasoning_text TEXT NOT NULL,
                rubric_score REAL NOT NULL,
                misconceptions TEXT,
                timestamp TEXT NOT NULL
            )
            """
        )


def save_attempt(
    scenario_id: str,
    numeric_answer: float,
    is_correct: bool,
    reasoning_text: str,
    rubric_score: float,
    misconceptions: list[str],
):
    timestamp = datetime.now().isoformat(timespec="seconds")

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            INSERT INTO learner_attempts (
                scenario_id,
                numeric_answer,
                is_correct,
                reasoning_text,
                rubric_score,
                misconceptions,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                scenario_id,
                numeric_answer,
                int(is_correct),
                reasoning_text,
                rubric_score,
                ", ".join(misconceptions),
                timestamp,
            ),
        )


def get_attempts():
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute(
            """
            SELECT *
            FROM learner_attempts
            ORDER BY id
            """
        )

        return cursor.fetchall()

if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized at {DB_PATH}")