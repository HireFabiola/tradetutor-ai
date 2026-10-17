"""Build the local knowledge collection from the approved course materials."""

from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHROMA_PATH = PROJECT_ROOT / "data/chroma_db"
COLLECTION_NAME = "tradetutor_knowledge"
CONTENT_DIRECTORIES = [PROJECT_ROOT / "data/lessons", PROJECT_ROOT / "data/knowledge"]


def load_chunks(filepath: str | Path) -> list[str]:
    text = Path(filepath).read_text(encoding="utf-8")
    return [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip() and not paragraph.strip().startswith("#")
    ]


def load_all_chunks(directories: list[str | Path]) -> list[dict]:
    return [
        {"text": chunk, "source": file.name}
        for directory in directories
        for file in sorted(Path(directory).glob("*.md"))
        for chunk in load_chunks(file)
    ]


def ingest_knowledge(collection, model, directories=CONTENT_DIRECTORIES) -> int:
    """Upsert course chunks so setup can safely be run more than once."""
    chunks = load_all_chunks(directories)
    if not chunks:
        raise ValueError("No course content was found for knowledge ingestion.")
    texts = [chunk["text"] for chunk in chunks]
    collection.upsert(
        ids=[f"chunk_{index}" for index in range(len(chunks))],
        documents=texts,
        embeddings=model.encode(texts).tolist(),
        metadatas=[{"source": chunk["source"]} for chunk in chunks],
    )
    return collection.count()


if __name__ == "__main__":
    model = SentenceTransformer("all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    count = ingest_knowledge(collection, model)
    print(f"ChromaDB contains {count} chunks.")
