import json
from typing import Dict, Any, List

from app.core.state import StoryState
from app.services.llm_provider import get_llm_provider
from app.prompts.loader import format_prompt