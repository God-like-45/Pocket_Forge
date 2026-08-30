import asyncio
import json
import sys
from app.agents.graph import app
from app.agents.state import AgentState

async def main():
    # Force UTF-8 for Windows console
    sys.stdout.reconfigure(encoding='utf-8')
    
    # A small piece of text featuring our seeded lore characters
    chapter_text = (
        "Dr. Aris stood by the viewport, staring out into the void. "
        "'The anti-gravity core is destabilizing,' he muttered, gripping the railing tightly. "
        "Captain Vance marched onto the bridge, adjusting his collar. "
        "'Then fix it, Doctor. We didn't come all this way to be crushed by our own ship.' "
        "The Aegis Core thrummed ominously beneath their feet, its silent hum feeling almost... angry."
    )
    
    initial_state = AgentState(
        chapter_text=chapter_text,
        director_breakdown=None,
        script=None,
        feedback=None,
        revision_count=0
    )
    
    print("Starting LangGraph Pipeline...\n")
    
    # We can run the compiled graph synchronously for this test
    # but since we're in async context we'll use ainvoke or run it via a thread if synchronous
    # `app.invoke` works fine here.
    final_state = app.invoke(initial_state)
    
    print("\n--- Final Output ---")
    print("Director Breakdown:")
    print(final_state.get("director_breakdown"))
    
    print("\nReviewer Feedback:")
    print(final_state.get("feedback"))
    
    print("\nFinal Script JSON:")
    if final_state.get("script"):
        print(final_state["script"].model_dump_json(indent=2))
    else:
        print("Failed to generate script.")

if __name__ == "__main__":
    asyncio.run(main())
