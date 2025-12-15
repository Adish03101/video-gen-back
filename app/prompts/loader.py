import yaml
from pathlib import Path
from typing import Dict, Any
from jinja2 import Template

BASE_DIR = Path(__file__).parent / "library"
#unnecesasry this part, only because i have written prompt wrong
class SafeDict(dict):
    """
    A helper dictionary that returns the original key wrapped in braces 
    if the key is missing. This prevents errors when formatting JSON prompts.
    """
    def __missing__(self, key):
        return '{' + key + '}'

def get_prompt_template(name: str) -> Dict[str, Any]:
    """
    Loads raw Yaml file. Checks for '{name}.yaml' directly.
    """
    # Simply look for "idea.yaml"
    file_path = BASE_DIR / f"{name}.yaml"

    if not file_path.exists():
        raise FileNotFoundError(f"Prompt template '{name}.yaml' not found at {file_path}")
    
    with open(file_path, encoding="utf-8") as file:
        try:
            prompt_data = yaml.safe_load(file)
            return prompt_data
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file '{file_path}': {e}")
        
def format_prompt(name: str, variables: Dict[str, Any]) -> Dict[str, str]:
    """
    1. Loads the prompt.
    2. Zips the variables into the template.
    3. Returns the final System and User messages.
    """
    # Remove version argument here
    data = get_prompt_template(name)

    # Support both "system/user" (My style) AND "role/template" (Old style)
    system_raw = data.get("system") or data.get("content", "")
    user_raw = data.get("user") or data.get("template", "")

    try:
        # Standard Python formatting
        system_template = Template(system_raw)
        user_template = Template(user_raw)
        
        formatted_system = system_template.render(**variables)
        formatted_user = user_template.render(**variables)
    except KeyError as e:
        raise ValueError(f"Missing variable in prompt '{name}': {e}")

    return {
        "system": formatted_system,
        "user": formatted_user
    }