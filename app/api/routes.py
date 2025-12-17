from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

# --- DB IMPORTS ---
from sqlmodel import Session, select
from app.database.database import get_session
from app.database.models import Project

# --- GRAPH IMPORTS ---
from app.services.workflow import app as graph_app
from app.core.model import StoryState
from app.core.schemas import (
    IdeaRequest, IdeaResponse,
    BeatRequest, BeatResponse,
    StructureRequest, StructureResponse,
    SceneRequest, SceneResponse,
    DialogueRequest, DialogueResponse,
    SaveProjectRequest
)

router = APIRouter()

# ==============================================================================
# 1. GRAPH EXECUTION LOGIC
# ==============================================================================

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
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    # 1. MEMORY PROTECTION
    current_snapshot = await graph_app.aget_state(config)

    if current_snapshot and current_snapshot.values:
        for key in protected_keys:
            if key not in inputs:
                inputs[key] = current_snapshot.values.get(key, [])

    # 2. TIME TRAVEL (Steering)
    anchor = NODE_ANCHORS.get(target_node)
    
    if not anchor:
        raise ValueError(f"Node '{target_node}' has no defined anchor in NODE_ANCHORS.")

    await graph_app.aupdate_state(config, inputs, as_node=anchor)
    
    # Run exactly one step
    result = await graph_app.ainvoke(None, config=config)
    
    return result


# ==============================================================================
# 2. GENERATION ENDPOINTS
# ==============================================================================

@router.post("/generate/ideas", response_model=IdeaResponse)
async def generate_ideas(req: IdeaRequest):
    inputs = {
        "topic": req.topic,
        "feedback": req.feedback,
    }

    if req.current_ideas:
        inputs["selected_idea"] = {
            "title": req.current_ideas.title,
            "idea": req.current_ideas.idea 
        }
    else:
        inputs["selected_idea"] = None
        if req.current_generated_ideas:
            inputs["generated_ideas"] = [
                {"title": i.title, "idea": i.idea} for i in req.current_generated_ideas
            ]
        else:
            inputs["generated_ideas"] = []

    config = {"configurable": {"thread_id": req.session_id}}
    state = await graph_app.ainvoke(inputs, config=config)
    
    raw_ideas = state.get("generated_ideas", [])
    cleaned_ideas = []
    
    for i in raw_ideas:
        cleaned_ideas.append({
            "title": i.get("title", "Untitled"),
            "idea": i.get("idea") or i.get("premise", "") 
        })

    return {"ideas": cleaned_ideas}


@router.post("/generate/beats", response_model=BeatResponse)
async def generate_beats(req: BeatRequest):
    inputs = {
        "selected_idea": {"title": req.title, "premise": req.idea},
        "beats": req.current_beats or [], 
        "feedback": req.feedback,
    }
    
    state = await execute_step(
        req.session_id, 
        "generate_beats", 
        inputs
    )
    return {"beats": state.get("beats", [])}


@router.post("/generate/structure", response_model=StructureResponse)
async def generate_structure(req: StructureRequest):
    inputs = {
        "beats": req.beats, 
        "selected_idea": {"title": req.title},
        "structure": req.current_structure.dict() if req.current_structure else None,
        "feedback": req.feedback,
    }
    
    state = await execute_step(
        req.session_id, 
        "organize_structure", 
        inputs
    )
    
    raw_structure = state.get("structure") or {}
    return {
        "structure": {
            "hook": raw_structure.get("hook", []),
            "mid": raw_structure.get("mid", []),
            "end": raw_structure.get("end", [])
        }
    }


@router.post("/generate/scenes", response_model=SceneResponse)
async def generate_scenes(req: SceneRequest):
    # 1. PARSE: Convert the input string ("Beat 1\nBeat 2") into a List
    # This ensures the Node has distinct items to loop through.
    beat_list = [b.strip() for b in req.structure_segment.split('\n') if b.strip()]

    # 2. SETUP INPUTS: align strictly with what scene_node expects
    inputs = {
        "selected_idea": {"title": req.title},
        
        # We manually populate the structure so the node finds state['structure']['hook']
        "structure": {
            req.current_section_name.lower(): beat_list
        },
        
        # Tell the node which key to read
        "current_section_name": req.current_section_name.lower(),
        
        "feedback": req.feedback,
        "scenes": req.current_scenes or [], 
        
        # Pass previous context (e.g., from Hook if we are doing Mid)
        "previous_context_override": req.previous_context 
    }

    # 3. EXECUTE
    state = await execute_step(
        req.session_id, 
        "generate_scenes", 
        inputs, 
        protected_keys=["all_scenes", "scenes_by_section"] 
    )
    
    return {"scenes": state.get("scenes", [])}

@router.post("/generate/dialogue", response_model=DialogueResponse)
async def generate_dialogue(req: DialogueRequest):
    inputs = {
        "current_scene": req.scene_content,
        "characters": req.characters,
        "feedback": req.feedback,
        "previous_dialogue": req.previous_dialogue,
    }
    
    # --- FIX: GHOST DIALOGUE BUG ---
    if req.current_dialogue:
        inputs["current_generated_dialogue"] = [
            line.dict() for line in req.current_dialogue
        ]
    else:
        # CRITICAL: Send empty list to force a wipe.
        # Sending 'None' causes LangGraph to keep the OLD dialogue.
        inputs["current_generated_dialogue"] = [] 

    state = await execute_step(
        req.session_id, 
        "generate_dialogue", 
        inputs, 
        protected_keys=["all_scenes", "all_dialogues"] 
    )
    
    raw_dialogue = state.get("current_generated_dialogue", [])
    
    cleaned_dialogue = []
    for line in raw_dialogue:
        cleaned_dialogue.append({
            "character": line.get("character", "Unknown"),
            "text": line.get("text", ""),
            "parenthetical": line.get("parenthetical") 
        })
    
    return {"dialogue": cleaned_dialogue}


# ==============================================================================
# 3. DATABASE ENDPOINTS (NEW)
# ==============================================================================
# Takes the full frontend state

@router.get("/projects")
async def list_projects(session: Session = Depends(get_session)):
    # List all projects, newest first
    statement = select(Project).order_by(Project.updated_at.desc())
    results = session.exec(statement).all()
    return results

@router.get("/projects/{project_id}")
async def get_project(project_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/projects/save")
async def save_project(req: SaveProjectRequest, session: Session = Depends(get_session)):
    if req.project_id:
        # UPDATE Existing
        project = session.get(Project, req.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project.title = req.title
        project.story_data = req.story_data
        project.updated_at = datetime.utcnow()
    else:
        # CREATE New
        project = Project(
            title=req.title, 
            story_data=req.story_data
        )
        session.add(project)
    
    session.commit()
    session.refresh(project)
    
    return {"status": "saved", "project_id": project.id, "title": project.title}