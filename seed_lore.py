import uuid
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.vector_store.qdrant_client import qdrant, get_embedding, embedding_model

COLLECTION_NAME = "lore_entities"

# Mock Sci-Fi Lore Data (Anti-gravity tech story)
LORE_DATA = [
    {
        "name": "Dr. Aris",
        "role": "Lead Scientist",
        "persona": "Brilliant but erratic physicist who first stabilized the graviton field.",
        "voice_tone": "Fast-paced, slightly breathless, highly analytical.",
        "stance": "Believes anti-gravity is the key to human ascension, ignores military applications."
    },
    {
        "name": "Captain Vance",
        "role": "Military Overseer",
        "persona": "Grizzled veteran tasked with securing the prototype at all costs.",
        "voice_tone": "Gravelly, commanding, impatient with scientific jargon.",
        "stance": "Views anti-gravity purely as a tactical advantage; deeply suspicious of Aris."
    },
    {
        "name": "The Aegis Core",
        "role": "Artifact",
        "persona": "Not a person, but the central piece of technology that enables localized anti-gravity.",
        "voice_tone": "N/A",
        "stance": "Emits a low hum; known to cause mild temporal distortions when over-clocked."
    }
]

def seed_database():
    print(f"Checking if collection '{COLLECTION_NAME}' exists...")
    
    # Recreate the collection
    if qdrant.collection_exists(COLLECTION_NAME):
        print(f"Collection '{COLLECTION_NAME}' exists. Deleting it...")
        qdrant.delete_collection(COLLECTION_NAME)

    print(f"Creating collection '{COLLECTION_NAME}'...")
    # Get the embedding dimension from the model (for all-MiniLM-L6-v2 it's 384)
    vector_size = embedding_model.get_sentence_embedding_dimension()
    
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

    print("Generating embeddings and indexing lore data...")
    points = []
    for entity in LORE_DATA:
        # Create a combined string of the entity's details to embed
        text_to_embed = f"{entity['name']}: {entity['role']}. {entity['persona']} Stance: {entity['stance']}"
        
        vector = get_embedding(text_to_embed)
        
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload=entity
            )
        )
    
    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print(f"Successfully inserted {len(points)} entities into '{COLLECTION_NAME}'.")

if __name__ == "__main__":
    seed_database()
