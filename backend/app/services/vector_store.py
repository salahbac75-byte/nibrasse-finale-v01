import chromadb
from chromadb.config import Settings

_chroma_client = None
_collection = None

def get_collection():
    global _chroma_client, _collection
    if _collection is None:
        _chroma_client = chromadb.PersistentClient(path="data/chroma_db")
        _collection = _chroma_client.get_or_create_collection(name="rag_collection")
    return _collection

def add_documents_to_chroma(ids: list[str], documents: list[str], metadatas: list[dict], embeddings: list[list[float]]):
    collection = get_collection()
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

def query_chroma(query_embedding: list[float], n_results: int = 5):
    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=['documents', 'distances', 'metadatas']
    )
    return results
