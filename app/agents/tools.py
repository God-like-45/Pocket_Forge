from langchain_core.tools import tool
from app.vector_store.qdrant_client import qdrant, get_embedding

@tool
def lore_rag_tool(character_name: str) -> str:
    """Queries the vector database for lore/persona information about a given character."""
    
    # Generate an embedding for the character name to find relevant documents
    query_vector = get_embedding(character_name)
    
    try:
        # Search the collection for the closest matches
        search_result = qdrant.search(
            collection_name="lore_entities",
            query_vector=query_vector,
            limit=2
        )
        
        if not search_result:
            return f"No lore found for '{character_name}'."
            
        # Combine the lore payload from the top results
        lore_info = []
        for hit in search_result:
            payload = hit.payload or {}
            entity = payload.get("entity_name", "Unknown Entity")
            persona = payload.get("persona", "")
            voice = payload.get("voice_tone", "")
            stance = payload.get("stance_on_tech", "")
            
            lore_info.append(
                f"Entity: {entity}\nPersona: {persona}\nVoice Tone: {voice}\nStance: {stance}"
            )
            
        return "\n\n---\n\n".join(lore_info)
        
    except Exception as e:
        return f"Error querying lore database: {str(e)}"
