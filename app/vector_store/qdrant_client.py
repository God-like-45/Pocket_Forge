import os
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Load environment variable or default to localhost
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6335")

# Initialize Qdrant client
qdrant = QdrantClient(url=QDRANT_URL)

_embedding_model = None

def get_embedding(text: str) -> list[float]:
    """Generates an embedding vector for the given text."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model.encode(text).tolist()
