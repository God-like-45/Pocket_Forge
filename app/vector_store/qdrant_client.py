import os
from qdrant_client import QdrantClient


# Use local file-based Qdrant database to avoid needing a dedicated cloud server
QDRANT_PATH = os.getenv("QDRANT_PATH", "./qdrant_data")

# Initialize Qdrant client in local mode
qdrant = QdrantClient(path=QDRANT_PATH)

_embedding_model = None

def get_embedding(text: str) -> list[float]:
    """Generates an embedding vector for the given text."""
    global _embedding_model
    if _embedding_model is None:
        from fastembed import TextEmbedding
        # BAAI/bge-small-en-v1.5 is the default and is very memory efficient
        _embedding_model = TextEmbedding()
    
    # fastembed returns a generator of numpy arrays, we need to extract the first one
    embeddings = list(_embedding_model.embed([text]))
    return embeddings[0].tolist()
