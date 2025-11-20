import chromadb
import os

def test_chroma():
    print("Initializing ChromaDB...")
    try:
        chroma_client = chromadb.PersistentClient(path="data/chroma_db_test")
        collection = chroma_client.get_or_create_collection(name="test_collection")
        
        print("Adding document...")
        collection.add(
            ids=["id1"],
            documents=["This is a test"],
            metadatas=[{"source": "test"}],
            embeddings=[[0.1] * 768] # Fake embedding
        )
        print("ChromaDB Success!")
    except Exception as e:
        print(f"ChromaDB Failed: {e}")

if __name__ == "__main__":
    test_chroma()
