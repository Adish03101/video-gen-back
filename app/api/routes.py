from fastapi import APIRouter, HTTPException
from app.services.workflow import app as graph_app  # The LangGraph App
from app.core.model import StoryState    
from typing import List


# Import the Schemas we designed for "Frontend Truth"
from app.core.schemas import (
    IdeaRequest, IdeaResponse,
    BeatRequest, BeatResponse,
    StructureRequest, StructureResponse,
    SceneRequest, SceneResponse,
    DialogueRequest, DialogueResponse
)

router = APIRouter()

NODE_ANCHORS = {
    "generate_beats": "generate_ideas",
    "organize_structure": "generate_beats",
    "generate_scenes": "organize_structure",
    "generate_dialogue": "generate_scenes"
}

async def execute_step(
    thread_id: str, 
    target_node: str, 
    inputs: dict, 
    protected_keys: List[str] = []
):
    """
    Universal function to run ANY node while preserving memory.
    
    :param thread_id: The session ID.
    :param target_node: The node we want to run (e.g., 'generate_scenes').
    :param inputs: The 'Frontend Truth' (User edits/feedback).
    :param protected_keys: Data we must NOT lose during time-travel (e.g., 'all_scenes').
    """
    config = {"configurable": {"thread_id": thread_id}}
    #memory
    current_snapshot = await graph_app.aget_state(config)

    
    if current_snapshot and current_snapshot.values:
        for key in protected_keys:
            if key not in inputs:
                inputs[key] = current_snapshot.values.get(key, [])

    # 2. TIME TRAVEL (Steering)
    anchor = NODE_ANCHORS.get(target_node)
    
    # Safety check: If node isn't mapped, we can't route to it
    if not anchor:
        raise ValueError(f"Node '{target_node}' has no defined anchor in NODE_ANCHORS.")

    await graph_app.aupdate_state(config, inputs, as_node=anchor)
    
    # Run exactly one step (stopped by interrupt_after in workflow.py)
    result = await graph_app.ainvoke(None, config=config)
    
    return result

@router.post("/generate/ideas", response_model=IdeaResponse)
async def generate_ideas(req: IdeaRequest):
    # 1. Prepare Inputs
    inputs = {
        "topic": req.topic,
        "feedback": req.feedback,
    }

    # 2. EXACT MAPPING: Frontend "idea" -> Backend "idea"
    # No more "premise" conversion.
    if req.current_ideas:
        inputs["selected_idea"] = {
            "title": req.current_ideas.title,
            "idea": req.current_ideas.idea 
        }
    else:
        inputs["selected_idea"] = None
        # Handle Reroll
        if req.current_generated_ideas:
            inputs["generated_ideas"] = [
                {"title": i.title, "idea": i.idea} for i in req.current_generated_ideas
            ]
        else:
            inputs["generated_ideas"] = []

    # 3. Run Graph
    config = {"configurable": {"thread_id": req.session_id}}
    state = await graph_app.ainvoke(inputs, config=config)
    
    # 4. Return Data
    # The Node might return 'premise' (because LLMs do that), 
    # so we still need a safe .get() here to catch it.
    raw_ideas = state.get("generated_ideas", [])
    cleaned_ideas = []
    
    for i in raw_ideas:
        cleaned_ideas.append({
            "title": i.get("title", "Untitled"),
            # Check 'idea' first. If LLM gave 'premise', use that.
            "idea": i.get("idea") or i.get("premise", "") 
        })

    return {"ideas": cleaned_ideas}

@router.post("/generate/beats", response_model=BeatResponse)
async def generate_beats(req: BeatRequest):
    # 1. Prepare Inputs
    # We map the Frontend request to the StoryState keys
    inputs = {
        # Context: The idea we are expanding
        "selected_idea": {"title": req.title, "premise": req.idea},
        
        # Edit Mode: If user sends beats, we put them in state so Node sees them
        "beats": req.current_beats or [], 
        
        "feedback": req.feedback,
    }
    
    # 2. Execute with Time Travel
    # "generate_beats" anchors to "generate_ideas" (it needs the idea to exist)
    state = await execute_step(
        req.session_id, 
        "generate_beats", 
        inputs
        # No protected_keys needed here because we re-injected the necessary context (selected_idea) above
    )
    
    # 3. Return
    return {"beats": state.get("beats", [])}


# --- STEP 3: STRUCTURE ---
@router.post("/generate/structure", response_model=StructureResponse)
async def generate_structure(req: StructureRequest):
    # 1. Prepare Inputs
    inputs = {
        # Context: Structure needs the Beats to organize them
        "beats": req.beats, 
        "selected_idea": {"title": req.title},
        
        # Edit Mode: If user sends a structure, inject it for the Node to refine
        # We use .dict() because structure is a Pydantic model in the request
        "structure": req.current_structure.dict() if req.current_structure else None,
        
        "feedback": req.feedback,
    }
    
    state = await execute_step(
        req.session_id, 
        "organize_structure", 
        inputs
    )
    
    # 3. Return (Handle potential None values safely)
    raw_structure = state.get("structure") or {}
    
    # Ensure we return valid lists even if the AI missed one
    return {
        "structure": {
            "hook": raw_structure.get("hook", []),
            "mid": raw_structure.get("mid", []),
            "end": raw_structure.get("end", [])
        }
    }

# --- STEP 4: SCENES (The Loop) ---
@router.post("/generate/scenes", response_model=SceneResponse)
async def generate_scenes(req: SceneRequest):
    # 1. Prepare Inputs
    # We construct a temporary structure dict just for this section so the Node focuses correctly.
    # The Node expects { "hook": "..." } or { "mid": "..." } based on current_section_name
    # But wait, your Schema sends 'structure_segment' as a string (the summary/beat list for that section).
    # We need to infer the section name or rely on the AI to figure it out? 
    # Better: We'll pass it generically and let the prompt handle it.
    
    # NOTE: Your schema lacks 'current_section_name' (e.g. "Hook"). 
    # We will assume 'structure_segment' contains the text the AI needs to expand.
    
    inputs = {
        "selected_idea": {"title": req.title},
        # We pass the raw segment text. The Node prompt needs to handle "Expand this segment".
        "structure": {"current_segment": req.structure_segment}, 
        
        "feedback": req.feedback,
        
        # Edit Mode: If user edits scenes manually, we pass them back
        "scenes": req.current_scenes or [], 
        
        # Context: Previous context (like summary of previous acts)
        "previous_context": req.previous_context
    }

    # 2. Execute with Time Travel & Protection
    # "all_scenes" MUST be protected. If we generate 'Mid', we don't want to lose 'Hook'.
    state = await execute_step(
        req.session_id, 
        "generate_scenes", 
        inputs, 
        protected_keys=["all_scenes"] 
    )
    
    # 3. Return
    # The Node should return the specific list of scenes for *this* segment
    return {"scenes": state.get("scenes", [])}


# --- STEP 5: DIALOGUE ---
@router.post("/generate/dialogue", response_model=DialogueResponse)
async def generate_dialogue(req: DialogueRequest):
    # 1. Prepare Inputs
    # Logic: Differentiate between "First Run" and "Edit/Refine"
    
    inputs = {
        # Context: The scene description we are writing dialogue for
        "current_scene": req.scene_content,
        
        # Context: Who is in the scene
        "characters": req.characters, # List[str]
        
        "feedback": req.feedback,
        
        # Context: What happened before (critical for continuity)
        "previous_dialogue": req.previous_dialogue,
    }
    
    # Edit Mode: If existing dialogue is sent, map it so the Node can edit it.
    if req.current_dialogue:
        # Convert Pydantic models -> Dicts for the Graph State
        inputs["current_generated_dialogue"] = [
            line.dict() for line in req.current_dialogue
        ]
    else:
        # Clear it so the node knows to generate fresh
        inputs["current_generated_dialogue"] = None

    # 2. Execute with Time Travel & Protection
    # We protect "all_dialogues" so we build a full script, not just one scene's worth.
    # We also protect "all_scenes" so we don't lose the scene list while focusing on dialogue.
    state = await execute_step(
        req.session_id, 
        "generate_dialogue", 
        inputs, 
        protected_keys=["all_scenes", "all_dialogues"] 
    )
    
    # 3. Return & Map
    # Graph returns Dicts, Pydantic expects DialogueLine objects.
    raw_dialogue = state.get("current_generated_dialogue", [])
    
    cleaned_dialogue = []
    for line in raw_dialogue:
        cleaned_dialogue.append({
            "character": line.get("character", "Unknown"),
            "text": line.get("text", ""),
            "parenthetical": line.get("parenthetical") 
        })
    
    return {"dialogue": cleaned_dialogue}