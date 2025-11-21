import json
from app.services.llm_provider import get_llm_provider
from app.prompts.loader import format_prompt
from app.core.schemas import (
    IdeaResponse, ScriptResponse, SceneResponse, DialogueResponse,
    IdeaRequest, ScriptRequest, SceneRequest, DialogueRequest
)

from app.core import memory

# ==========================================
# 1. Generate Video Ideas
# ==========================================

async def generate_video_ideas(request: IdeaRequest, count: int = 5) -> IdeaResponse:
    """
    Orchestrates the brainstorming process.
    Accepts optional chat history for refinements.
    """
    history = memory.get_history(request.session_id)

    # 1. Get the AI (Groq for now)
    provider = get_llm_provider("idea")
    
    # 2. Prepare the Prompt
    prompt_messages = format_prompt(
        name="idea",
        variables={
            "topic": request.topic,
            "audience": request.audience or "General Audience",
            "count": count
        }
    )
    
    # 3. Call the AI (Passing History!)
    raw_data = provider.generate(
        system_prompt=prompt_messages["system"], 
        user_prompt=prompt_messages["user"], 
        history=history
    )
    
    if request.session_id:
        # Save User's actual question text
        memory.add_message(request.session_id, "user", prompt_messages["user"])
        # Save AI's response (as JSON string)
        memory.add_message(request.session_id, "assistant", json.dumps(raw_data))

    # 4. Validate & Return
    return IdeaResponse(**raw_data)


# ==========================================
# 2. Generate Video Script
# ==========================================
async def generate_video_script(request: ScriptRequest) -> ScriptResponse:
    """
    Orchestrates writing the full script.
    Calculates word counts and accepts history for rewrites.
    """
    history = memory.get_history(request.session_id)

    provider = get_llm_provider("script")
    
    # Logic: Convert Duration (seconds) to Word Count
    # Standard speaking rate is ~150 words per minute (2.5 words/sec)
    duration = request.target_duration or 60
    word_count = int(duration * 2.5)
    
    prompt_messages = format_prompt(
        name="script",
        variables={
            "title": request.title,
            "tone": request.tone or "Engaging",
            "duration": duration,
            "word_count": word_count
        }
    )
    
    raw_data = provider.generate(
        system_prompt=prompt_messages["system"], 
        user_prompt=prompt_messages["user"],
        history=history
    )

    if request.session_id:
        # Save User's actual question text
        memory.add_message(request.session_id, "user", prompt_messages["user"])
        # Save AI's response (as JSON string)
        memory.add_message(request.session_id, "assistant", json.dumps(raw_data))

    return ScriptResponse(**raw_data)


# ==========================================
# 3. Generate Scene Prompts (Visuals)
# ==========================================
async def generate_scene_prompts(request: SceneRequest) -> SceneResponse:
    """
    Converts a script segment into an Image Generation Prompt.
    """
    history = memory.get_history(request.session_id)


    provider = get_llm_provider("scene")
    
    prompt_messages = format_prompt(
        name="scene",
        variables={
            "script_segment": request.script_segment,
            "style": request.art_style or "Cinematic"
        }
    )
    
    raw_data = provider.generate(
        system_prompt=prompt_messages["system"], 
        user_prompt=prompt_messages["user"],
        history=history
    )

    if request.session_id:
        # Save User's actual question text
        memory.add_message(request.session_id, "user", prompt_messages["user"])
        # Save AI's response (as JSON string)
        memory.add_message(request.session_id, "assistant", json.dumps(raw_data))

    return SceneResponse(**raw_data)


# ==========================================
# 4. Generate Dialogue (Audio)
# ==========================================
async def generate_dialogue(request: DialogueRequest) -> DialogueResponse:
    """
    Writes the spoken lines for characters.
    """
    history = memory.get_history(request.session_id)

    provider = get_llm_provider("dialogue")
    
    # Helper Logic: Join List ["Alice", "Bob"] -> String "Alice, Bob"
    char_str = ", ".join(request.characters)
    
    prompt_messages = format_prompt(
        name="dialogue",
        variables={
            "characters": char_str,
            "context": request.context
        }
    )
    
    raw_data = provider.generate(
        system_prompt=prompt_messages["system"], 
        user_prompt=prompt_messages["user"],
        history=history
    )

    if request.session_id:
        # Save User's actual question text
        memory.add_message(request.session_id, "user", prompt_messages["user"])
        # Save AI's response (as JSON string)
        memory.add_message(request.session_id, "assistant", json.dumps(raw_data))

    return DialogueResponse(**raw_data)