import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="data/chroma_db")

collection = client.get_collection(
    name="tradetutor_knowledge"
)

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