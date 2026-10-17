import chromadb
from sentence_transformers import SentenceTransformer
from app.rag.embedder import CHROMA_PATH, COLLECTION_NAME, ingest_knowledge

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=str(CHROMA_PATH))

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)

if collection.count() == 0:
    ingest_knowledge(collection, model)

def retrieve_chunks(query: str, n_results: int = 3):
    query_embedding = model.encode(query)

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    return results

if __name__ == "__main__":
    query = "Why is win rate important when evaluating a trading strategy?"

    results = retrieve_chunks(query)

    print(f"\nQUERY:\n{query}")
    print("\nTOP MATCHES:")

    for document, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        print(f"\nDistance: {distance:.4f}")
        print(f"Source: {metadata['source']}")
        print(f"Text: {document}")
