from typing import TypedDict, Optional, List
from app.schemas.script import Script

class AgentState(TypedDict):
    chapter_text: str
    director_breakdown: Optional[str]
    script: Optional[Script]
    feedback: Optional[str]
    revision_count: int
