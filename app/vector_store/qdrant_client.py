import os
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Use local file-based Qdrant database to avoid needing a dedicated cloud server
QDRANT_PATH = os.getenv("QDRANT_PATH", "./qdrant_data")

# Initialize Qdrant client in local mode
qdrant = QdrantClient(path=QDRANT_PATH)

_embedding_model = None

def get_embedding(text: str) -> list[float]:
    """Generates an embedding vector for the given text."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model.encode(text).tolist()
