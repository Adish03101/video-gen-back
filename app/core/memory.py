from typing import List, Dict, Optional, Any

# ==========================================
# 1. THE IN-MEMORY STORE
# ==========================================
# This global dictionary holds all chat history.
# Key: session_id (str)
# Value: List of messages [{"role": "user", "content": "..."}]
SESSION_STORE: Dict[str, List[Dict[str, Any]]] = {}

# ==========================================
# 2. RETRIEVAL FUNCTION
# ==========================================
def get_history(session_id: Optional[str]) -> List[Dict[str, Any]]:
    """
    Retrieves the entire conversation history for a given session ID.
    Returns an empty list if the session ID is not found or is None.
    """
    if not session_id:
        return []
    
    # Use .get() to safely retrieve the list, defaulting to an empty list
    return SESSION_STORE.get(session_id, [])

# ==========================================
# 3. STORAGE FUNCTION
# ==========================================
def add_message(session_id: str, role: str, content: Any):
    """
    Adds a new message (user or assistant) to the session history.
    """
    if not session_id:
        return
        
    # Ensure the session exists in the store
    if session_id not in SESSION_STORE:
        SESSION_STORE[session_id] = []
        
    # Add the new message
    SESSION_STORE[session_id].append({
        "role": role,
        # Content can be a string (user) or a JSON string (assistant output)
        "content": content
    })
    
    # OPTIONAL: Keep history manageable (e.g., limit to the last 20 messages)
    MAX_MESSAGES = 20
    if len(SESSION_STORE[session_id]) > MAX_MESSAGES:
        SESSION_STORE[session_id] = SESSION_STORE[session_id][-MAX_MESSAGES:]