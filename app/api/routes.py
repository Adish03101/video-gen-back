from fastapi import APIRouter, HTTPException
from typing import List, Any

# 1. Import all Schemas (The Contract/Bouncers)
from app.core.schemas import (
    IdeaRequest, IdeaResponse,
    ScriptRequest, ScriptResponse,
    SceneRequest, SceneResponse,
    DialogueRequest, DialogueResponse
)

# 2. Import your Logic (The Chefs - Corrected to llm_engine)
from app.services.llm_engine import (
    generate_video_ideas,
    generate_video_script,
    generate_scene_prompts,
    generate_dialogue
)

router = APIRouter()

# ==========================================
# 1. Video Ideas Endpoint
# ==========================================
@router.post("/video/ideas", response_model=IdeaResponse)
async def create_video_ideas(request: IdeaRequest):
    """
    Generate video ideas based on a topic and audience.
    """
    try:
        # We pass the request object. The generator function (in llm_engine) 
        # is responsible for checking request.session_id and retrieving history.
        return await generate_video_ideas(request, count=5)
    except Exception as e:
        # Ensure proper error message propagation
        raise HTTPException(status_code=500, detail=f"Idea Generation Failed: {str(e)}")
    
# ==========================================
# 2. Script Generation Endpoint
# ==========================================
@router.post("/video/script", response_model=ScriptResponse)
async def create_video_script(request: ScriptRequest):
    """
    Generate a full script for a specific idea.
    """
    try:
        return await generate_video_script(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Script Generation Failed: {str(e)}")
    
# ==========================================
# 3. Scene Generation Endpoint
# ==========================================
@router.post("/video/scene", response_model=SceneResponse)
async def create_video_scene(request: SceneRequest):
    """
    Turn a script segment into an image prompt.
    """
    try:
        # Note the change in function name call to match your generator logic
        return await generate_scene_prompts(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scene Prompt Generation Failed: {str(e)}")
    
# ==========================================
# 4. Dialogue Generation Endpoint
# ==========================================
@router.post("/video/dialogue", response_model=DialogueResponse)
async def create_video_dialogue(request: DialogueRequest):
    """
    Generate spoken dialogue lines for characters.
    """
    try:
        return await generate_dialogue(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dialogue Generation Failed: {str(e)}")