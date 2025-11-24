import pickle
import os
from rank_bm25 import BM25Okapi
from typing import List, Tuple

INDEX_FILE = "data/bm25_index.pkl"

class BM25Service:
    def __init__(self):
        self.bm25 = None
        self.corpus = [] # List of texts (chunks)
        self.metadatas = [] # List of metadata corresponding to chunks
        self.load_index()

    def build_index(self, corpus: List[str], metadatas: List[dict]):
        """Builds and saves the BM25 index."""
        tokenized_corpus = [doc.split(" ") for doc in corpus]
        self.bm25 = BM25Okapi(tokenized_corpus)
        self.corpus = corpus
        self.metadatas = metadatas
        self.save_index()

    def save_index(self):
        """Saves the index and corpus to disk."""
        os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
        with open(INDEX_FILE, "wb") as f:
            pickle.dump({
                "bm25": self.bm25,
                "corpus": self.corpus,
                "metadatas": self.metadatas
            }, f)

    def load_index(self):
        """Loads the index from disk if it exists."""
        if os.path.exists(INDEX_FILE):
            try:
                with open(INDEX_FILE, "rb") as f:
                    data = pickle.load(f)
                    self.bm25 = data["bm25"]
                    self.corpus = data["corpus"]
                    self.metadatas = data.get("metadatas", [])
            except Exception as e:
                print(f"Error loading BM25 index: {e}")

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float, dict]]:
        """
        Search the corpus using BM25.
        Returns a list of (chunk, score, metadata) tuples.
        """
        if not self.bm25:
            return []

        tokenized_query = query.split(" ")
        # Get scores for all documents
        scores = self.bm25.get_scores(tokenized_query)
        
        # Pair scores with docs and metadata
        results = []
        for i, score in enumerate(scores):
            if score > 0:
                results.append((self.corpus[i], score, self.metadatas[i] if i < len(self.metadatas) else {}))
        
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:top_k]

# Global instance
bm25_service = BM25Service()
