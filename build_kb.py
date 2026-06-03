# build_kb.py
# Run this ONCE to build the ChromaDB knowledge base
# Usage: python build_kb.py

# build_kb.py
# Run ONCE to build ChromaDB — uses ChromaDB directly, no langchain-community

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from src.ingest import load_constitution

CHROMA_PATH = "chroma_db"
EMBEDDING_MODEL = "law-ai/InLegalBERT"

def build():
    print("=" * 50)
    print("Building Constitution Knowledge Base")
    print("=" * 50)

    # Load and chunk the PDF
    documents = load_constitution()

    print(f"\nLoading embedding model: {EMBEDDING_MODEL}")
    ef = SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )

    print("Setting up ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Delete existing collection if rebuilding
    try:
        client.delete_collection("constitution")
        print("Deleted old collection")
    except:
        pass

    collection = client.create_collection(
        name="constitution",
        embedding_function=ef
    )

    # Add documents in batches of 50
    print(f"\nEmbedding {len(documents)} chunks...")
    batch_size = 50

    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        collection.add(
            ids=[f"doc_{i+j}" for j in range(len(batch))],
            documents=[d.page_content for d in batch],
            metadatas=[d.metadata for d in batch]
        )
        print(f"  Embedded {min(i+batch_size, len(documents))}/{len(documents)} chunks")

    print(f"\nDone! Knowledge base saved to '{CHROMA_PATH}/'")
    print(f"Total chunks: {len(documents)}")
    print("\nNow run: streamlit run app.py")

if __name__ == "__main__":
    build()