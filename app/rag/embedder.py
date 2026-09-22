
import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="data/chroma_db")

collection = client.get_or_create_collection(
    name="tradetutor_knowledge"
)

def load_chunks(filepath: str) -> list[str]:
    with open(filepath, "r") as f:
        text = f.read()

    raw_paragraphs = text.split("\n\n")
    chunks = [p.strip() for p in raw_paragraphs if p.strip() and not p.strip().startswith("#")]
    return chunks


def load_all_chunks(directories: list[str]) -> list[dict]:
    all_chunks = []
    for directory in directories:
        for file in Path(directory).glob("*.md"):
            chunks = load_chunks(file)
            for chunk in chunks:
                all_chunks.append({"text": chunk, "source": file.name})
    return all_chunks


if __name__ == "__main__":
    all_chunks = load_all_chunks(["data/lessons", "data/knowledge"])

    texts = [chunk["text"] for chunk in all_chunks]
    embeddings = model.encode(texts)

    ids = [f"chunk_{i}" for i in range(len(all_chunks))]

    metadatas = [
    {"source": chunk["source"]}
    for chunk in all_chunks
    ]

#     collection.add(
#     ids=ids,
#     documents=texts,
#     embeddings=embeddings.tolist(),
#     metadatas=metadatas
# )

    print(f"ChromaDB contains {collection.count()} chunks.")