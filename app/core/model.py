from typing import TypedDict, Any, Dict, List, Optional

class StoryState(TypedDict):
   #input
    topic: str
    feedback: Optional[str]  # Critical: If this exists, Nodes enter "Edit Mode"
    
    #ideas
    generated_ideas: List[Dict]   # The menu of 3 options
    selected_idea: Optional[Dict] # The specific choice (Title/Premise)
    returned_idea: Optional[Dict]  # The idea returned from LLM (for edit mode)
#   beats
    beats: Optional[List[str]]    # The timeline of events
    
    #STRUCTURE
    structure: Optional[Dict]     # {"hook": [...], "mid": [...], "end": [...]}
    
    #SCENES (The Loop) 
    scenes_by_section: Optional[Dict[str, List[str]]]
    all_scenes: List[Dict[str, Any]]  # Each scene with context
    scenes: Optional[List[str]]  
    # DIALOGUE 
    all_dialogues: List[Dict[str, Any]]
    current_scene_index: Optional[int]
    current_generated_dialogue: Optional[List[Dict[str, str]]]
