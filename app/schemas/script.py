from pydantic import BaseModel, Field
from typing import List

class ScriptLine(BaseModel):
    speaker: str = Field(description="The name of the character speaking. Use 'NARRATOR' for narration.")
    text: str = Field(description="The actual text to be spoken.")
    emotion: str = Field(description="The emotional tone of the speaker, e.g., 'calm', 'angry', 'terrified', 'analytical'.")
    sfx: str | None = Field(default=None, description="Optional sound effect to play at the START of this line (e.g. 'explosion', 'door', 'alarm', 'laser').")

class Script(BaseModel):
    bgm_track: str = Field(description="The overall background music track for this scene. Must be one of: 'tense', 'action', 'calm'.")
    lines: List[ScriptLine] = Field(description="The list of script lines in chronological order.")
