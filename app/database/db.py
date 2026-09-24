import sqlite3
from pathlib import Path


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
    timestamp: str,
):
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


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized at {DB_PATH}")