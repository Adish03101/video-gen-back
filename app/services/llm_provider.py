import json
from abc import ABC, abstractmethod
from typing import Dict, Any
from groq import Groq
from app.config import settings

# ==========================================
# LAYER 1: The Interface (The Rules)
# ==========================================
class LLMProvider(ABC):
    """
    The Universal Contract.
    Every AI provider (Groq, Local, OpenAI) MUST follow these rules.
    """
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        pass

# ==========================================
# LAYER 2: The Groq Implementation
# ==========================================
class GroqProvider(LLMProvider):
    """
    The 'Active' provider using the Groq API.
    """
    def __init__(self):
        # Correctly initializing the client
        self.client = Groq(api_key=settings.GROQ_API)
        self.model = settings.LLM_MODEL  # e.g. "llama3-70b-8192"

    def generate(self, system_prompt: str, user_prompt: str, history: list = None) -> Dict[str, Any]:
        messages = [{"role": "system", "content": system_prompt}]

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": user_prompt})
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                # Force JSON mode for reliability
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            # Correct access method for Groq/OpenAI v1+ objects (dot notation)
            content = response.choices[0].message.content
            
            # Parse string -> JSON
            return json.loads(content)
            
        except json.JSONDecodeError:
            raise ValueError("AI returned invalid JSON. Check your prompts.")
        except Exception as e:
            raise RuntimeError(f"Groq API Error: {str(e)}")

# ==========================================
# LAYER 3: The Factory (The Router)
# ==========================================
def get_llm_provider(task_type: str) -> LLMProvider:
    """
    Decides which AI to use based on the task.
    Args:
        task_type: 'idea_gen', 'script_gen', 'dialogue_gen', 'scene_gen'
    """
    # Future logic for Local GPU will go here
    # if task_type == "dialogue_gen": return LocalProvider()
    
    
    return GroqProvider()