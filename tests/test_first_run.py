"""Verify first-run persistence using isolated local databases."""

import chromadb
import numpy as np

from app.database import db
from app.rag.embedder import ingest_knowledge
from app.services.attempt_service import process_attempt


class LocalTestEncoder:
    """Small deterministic embeddings keep persistence tests offline."""

    def encode(self, texts):
        return np.array([[float(len(text)), 1.0, 0.0] for text in texts])


def test_first_practice_submission_creates_database(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "data" / "attempts.db")
    assert db.get_attempts() == []
    # Exercise submission against a genuinely absent database as well.
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "fresh" / "attempts.db")
    result = process_attempt(
        scenario_id="meridian_001",
        entry_price=60,
        stop_loss_price=54,
        target_price=78,
        numeric_answer=3.0,
        reasoning_text="I risk $6 for a potential reward of $18.",
    )
    assert result["is_correct"] is True
    assert len(db.get_attempts()) == 1
    db.initialize_database()
    assert len(db.get_attempts()) == 1


def test_ingestion_persists_searchable_chunks_and_can_repeat(tmp_path):
    content = tmp_path / "lessons"
    content.mkdir()
    (content / "lesson.md").write_text(
        "# Lesson\n\nRisk is entry minus stop loss.\n\nReward is target minus entry.",
        encoding="utf-8",
    )
    client = chromadb.PersistentClient(path=str(tmp_path / "chroma"))
    collection = client.get_or_create_collection("test_knowledge")
    assert collection.count() == 0
    encoder = LocalTestEncoder()
    assert ingest_knowledge(collection, encoder, [content]) == 2
    assert ingest_knowledge(collection, encoder, [content]) == 2
    results = collection.query(query_embeddings=[[1.0, 1.0, 0.0]], n_results=2)
    assert set(results["documents"][0]) == {
        "Risk is entry minus stop loss.", "Reward is target minus entry."
    }
    assert all(item["source"] == "lesson.md" for item in results["metadatas"][0])
