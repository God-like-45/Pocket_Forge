import os
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Load environment variable or default to localhost
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6335")

# Initialize Qdrant client
qdrant = QdrantClient(url=QDRANT_URL)

# Load the HuggingFace model for embeddings (it will download on first run)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text: str) -> list[float]:
    """Generates an embedding vector for the given text."""
    return embedding_model.encode(text).tolist()
