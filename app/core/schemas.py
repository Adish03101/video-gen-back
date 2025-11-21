#a sort of check for the incomming data for each model
#will be helpful in db as well, if we add
#should focus on input and output both type of validation for
#schema

from pydantic import BaseModel
from typing import Optional, List


class BaseRequest(BaseModel):
    # This ID will be used to track the conversation in app/core/memory.py
    session_id: Optional[str] = None 

class IdeaRequest(BaseRequest):
    topic: str
    audience: Optional[str] = "General Audience"

class ScriptRequest(BaseRequest):
    title: str                 # "Space Cats"
    tone: Optional[str] = "Fun"
    target_duration: Optional[int] = 60


class SceneRequest(BaseRequest):
    script_segment: str     # Required: "The astronaut floats in the void, looking at earth."
    art_style: Optional[str] = "Cinematic" # Optional: "Anime", "Oil Painting", "Cyberpunk"

class DialogueRequest(BaseRequest):
    characters: List[str]   # ["Alice", "Bob"]
    context: str            # "Alice discovers Bob ate the last slice of pizza."
    style: Optional[str] = "Natural"


# OUTPUT helper
class DialogueLine(BaseModel):
    character_name: str
    text: str
    emotion: Optional[str] = "Neutral"

# OUTPUT
class DialogueResponse(BaseModel):
    dialogue: List[DialogueLine]

class IdeaItem(BaseModel):
    title: str          # "Space Pizza Party"
    description: str    # "A comedy about an astronaut ordering delivery to Mars."

class IdeaResponse(BaseModel):
    ideas: List[IdeaItem]

class ScriptSection(BaseModel):
    heading: str    # "Intro", "Scene 1", "Climax"
    content: str    # The actual narration/dialogue text for this part

class ScriptResponse(BaseModel):
    title: str
    full_script: str                # The whole thing combined (for easy copy-paste)
    sections: List[ScriptSection]   # Broken down parts
    characters_detected: List[str]  # ["Alice", "Bob"] - Auto-extracted for next step

class SceneResponse(BaseModel):
    image_prompt: str          # "Cinematic wide shot of a cat in a space suit, 8k, nebula background"
    art_style: str             # "Pixar 3D" (Just to confirm the style used)
    negative_prompt: Optional[str] = None # "blurry, distorted, text, watermark" (Useful for local models)