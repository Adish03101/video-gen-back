#a sort of check for the incomming data for each model
#will be helpful in db as well, if we add
#should focus on input and output both type of validation for
#schema

from pydantic import BaseModel
from typing import Optional, List


class BaseRequest(BaseModel):
    # This ID will be used to track the conversation in app/core/memory.py
    session_id: Optional[str]



class IdeaItem(BaseModel):
    title: str
    idea: str

class IdeaRequest(BaseRequest):
    topic: str
    feedback: Optional[str]
    current_ideas: Optional[IdeaItem] = None
    current_generated_ideas: Optional[List[IdeaItem]] = None


class IdeaResponse(BaseModel):
    ideas: List[IdeaItem]

class BeatRequest(BaseRequest):
    title: str
    idea: str
    feedback: Optional[str]
    current_beats: Optional[List[str]]

class BeatResponse(BaseModel):
    beats: List[str]

class StructureModel(BaseModel):
    hook: List[str]
    mid: List[str]
    end: List[str]

class StructureRequest(BaseRequest):
    title: str
    beats: List[str]
    feedback: Optional[str]
    current_structure: Optional[StructureModel] = None
    
class StructureResponse(BaseModel):
    structure: StructureModel

class SceneRequest(BaseRequest):
    title: str
    structure_segment: str
    previous_context: Optional[str] = None
    feedback: Optional[str]
    current_scenes: Optional[List[str]]

class SceneResponse(BaseModel):
    scenes: List[str]
    
class DialogueLine(BaseModel):
    character: str
    text: str
    parenthetical: Optional[str] = None # e.g. (whispering)

class DialogueRequest(BaseRequest):
    scene_content: str 
    
    characters: List[str]
    
    previous_dialogue: Optional[str] = None
    
    feedback: Optional[str] = None
    current_dialogue: Optional[List[DialogueLine]] = None

class DialogueResponse(BaseModel):
    # If this list is empty [], it means the scene is silent/action-only.
    dialogue: List[DialogueLine]