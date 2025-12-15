import json
from typing import Dict, Any, List

from app.core.model import StoryState
from app.services.llm_provider import get_llm_provider
from app.prompts.loader import format_prompt


def idea_node(state: StoryState):
    """
    Docstring for story_node
    
    :param state: Description
    :type state: StoryState
    """
    llm = get_llm_provider("story_gen")

    feedback = state.get('feedback', '')
    selected = state.get('selected_idea') or {} 
    previous_ideas = state.get('generated_ideas') or []
    context_instruction = ""

    if selected and (selected.get('premise') or selected.get('idea')):
        premise = selected.get('premise') or selected.get('idea')
        context_instruction = f"CURRENT DRAFT TO EDIT: {premise}"
        
    # Else, check if we have previous ideas + feedback (User wants Reroll)
    elif previous_ideas and feedback:
        context_instruction = f"PREVIOUS REJECTED IDEAS: {json.dumps(previous_ideas)}"

    prompt_vars = {
        "topic": state.get('topic', ''),
        "count": 2,
        # We format the instruction here so the YAML is clean
        "feedback_instruction": f"USER FEEDBACK: {feedback}" if feedback else "",
        # If editing, we show what we are editing. If creating, it's empty.
        "context_instruction": context_instruction
        }

    prompt_messages = format_prompt("idea", prompt_vars)

    raw_response = llm.generate(
        system_prompt=prompt_messages["system"],
        user_prompt=prompt_messages["user"]
    )

    new_ideas = raw_response.get("ideas", [])

    return {
        "generated_ideas": new_ideas,
        "feedback": None # Reset the "Hot Potato" so we don't get stuck in edit mode
    }

def beat_node(state: StoryState):
    llm = get_llm_provider("beat_gen")
    feedback = state.get('feedback', '')
    prompt_vars = {
        "title": state.get('title', ''),
        "idea": state.get('selected_idea', {}),
        "feedback_instruction": f"USER FEEDBACK: {feedback}" if feedback else "",
        "context_instruction": f"CURRENT BEATS: {state.get('beats')}" if feedback else ""
    }
    prompt_messages = format_prompt("beat", prompt_vars)

    raw_response = llm.generate(
        system_prompt=prompt_messages["system"],
        user_prompt=prompt_messages["user"]
    )
    new_beats = raw_response.get("beats", [])

    return {
        "beats": new_beats,
        "feedback": None  # Reset feedback after processing
    }

def structure_node(state: StoryState):
    # 1. SETUP
    llm = get_llm_provider("structure")
    feedback = state.get('feedback')
    selected = state.get('selected_idea', {})
    #as we are getting list of beats, we need to convert to string
    raw_beats = state.get('beats', [])
    beats_str = "\n".join([f"- {b}" for b in raw_beats])
    
    prompt_vars = {
        "title": selected.get('title', 'Untitled'),
        "beats_list": beats_str,
        
        "feedback_instruction": f"USER FEEDBACK: {feedback}" if feedback else "",
        "context_instruction": f"CURRENT STRUCTURE: {state.get('structure')}" if feedback else ""
    }

    prompt_messages = format_prompt("structure", prompt_vars)
    
    raw_response = llm.generate(
        system_prompt=prompt_messages["system"],
        user_prompt=prompt_messages["user"]
    )
    
    # Expected Output: { "structure": { "hook": [...], "mid": [...], "end": [...] } }
    new_structure = raw_response.get("structure", {})

    return {
        "structure": new_structure,
        "feedback": None
    }

def scene_node(state: StoryState):
    llm = get_llm_provider("scene")
    feedback = state.get('feedback')
    selected = state.get('selected_idea', {})

    section_name = state.get('current_section_name', 'hook').lower()
    
    segment_beats = state['structure'].get(section_name, [])
    segment_str = "\n".join(segment_beats)
    
    previous_scenes = state.get('all_scenes', [])

    current_buckets = state.get('scenes_by_section', {})
    
    context_list = []
    for sec in ['hook', 'mid', 'end']:
        if sec == section_name:
            break
        context_list.extend(current_buckets.get(sec, []))
    
    context_str = "\n".join(context_list) if context_list else "None, start of story."
    

    prompt_vars = {
        "title": selected.get('title', 'Untitled'),
        "structure_segment": segment_str, # The beats to adapt
        "previous_context": context_str,  # What happened before
        
        "feedback_instruction": f"USER FEEDBACK: {feedback}" if feedback else "",
        "context_instruction": "" 
    }

    prompt_messages = format_prompt("scene", prompt_vars)
    
    raw_response = llm.generate(
        system_prompt=prompt_messages["system"],
        user_prompt=prompt_messages["user"]
    )
    
    new_scenes = raw_response.get("scenes", [])
    
    # 6. UPDATE STATE (Cumulative Append)
    # We add the new scenes to our Master List.
    # NOTE: In a perfect world, if editing, you'd replace the old ones. 
    # For now, we append to keep it simple.
    updated_buckets = current_buckets.copy()
    updated_buckets[section_name] = new_scenes
    updated_all_scenes = []
    for sec in ['hook', 'mid', 'end']:
        updated_all_scenes.extend(updated_buckets.get(sec, []))
    return {
        "all_scenes": updated_all_scenes,
        "scenes": new_scenes, # We also return just this batch for the frontend to see
        "feedback": None
    }

def dialogue_node(state: StoryState):
    llm = get_llm_provider("dialogue")
    feedback = state.get('feedback')
    
    current_idx = state.get('current_scene_index', 0)
    all_scenes = state.get('all_scenes', [])
    
    # Safety Check: Does this index exist?
    if current_idx < 0 or current_idx >= len(all_scenes):
        raise ValueError(f"Scene Index {current_idx} is out of bounds. Total scenes: {len(all_scenes)}")
        
    current_scene_text = all_scenes[current_idx]
    all_dialogues = state.get('all_dialogues', [])
    
    sorted_history = sorted(all_dialogues, key=lambda x: x['scene_index'])
    
    history_str = ""
    for entry in sorted_history:
        if entry['scene_index'] >= current_idx:
            break
            
        lines_list = entry.get('lines', [])
        formatted_lines = " ".join([f"{l['character']}: {l['text']}" for l in lines_list])
        history_str += f"SCENE {entry['scene_index']}: {formatted_lines}\n\n"
        
    if not history_str:
        history_str = "None (Opening Scene)"

    prompt_vars = {
        "scene_content": current_scene_text,
        
        "characters": "Infer strictly from the Scene Context provided.", 
        
        "previous_dialogue": history_str,
        "feedback_instruction": f"USER FEEDBACK: {feedback}" if feedback else "",
        "context_instruction": "" 
    }

    prompt_messages = format_prompt("dialogue", prompt_vars)
    
    raw_response = llm.generate(
        system_prompt=prompt_messages["system"],
        user_prompt=prompt_messages["user"]
    )
    
    # Expected Output: [{"character": "Bob", "text": "Hi.", "parenthetical": "smiling"}]
    new_dialogue_lines = raw_response.get("dialogue", [])
    
    updated_all_dialogues = [d for d in all_dialogues if d['scene_index'] != current_idx]
    
    # Add the new entry
    new_entry = {
        "scene_index": current_idx,
        "lines": new_dialogue_lines
    }
    updated_all_dialogues.append(new_entry)

    return {
        "all_dialogues": updated_all_dialogues,
        "current_generated_dialogue": new_dialogue_lines, # For the Frontend
        "feedback": None
    }

def route_request(state: StoryState):
    """
    Decides which node to run based on the input.
    """
    # If we have a section name (like 'hook'), go to SCENES
    if state.get("current_section_name"):
        return "generate_scenes"
    
    # If we have a scene index (like 0, 1), go to DIALOGUE
    if state.get("current_scene_index") is not None:
        return "generate_dialogue"

    # If we have beats but no structure, go to STRUCTURE
    if state.get("beats") and not state.get("structure"):
        return "organize_structure"
        
    # If we have an idea, go to BEATS
    if state.get("selected_idea"):
        return "generate_beats"

    # Default: Start at IDEAS
    return "generate_ideas"