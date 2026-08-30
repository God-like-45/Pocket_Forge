from pydantic import BaseModel, Field
from typing import List

class ScriptLine(BaseModel):
    speaker: str = Field(description="The name of the character speaking. Use 'NARRATOR' for narration.")
    text: str = Field(description="The actual text to be spoken.")
    emotion: str = Field(description="The emotional tone of the speaker, e.g., 'calm', 'angry', 'terrified', 'analytical'.")

class Script(BaseModel):
    lines: List[ScriptLine] = Field(description="The list of script lines in chronological order.")
