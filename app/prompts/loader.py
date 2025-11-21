#a clear way of loading prompts

import yaml
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).parent / "library"

def get_prompt_template(name: str, version: str = 'v1') -> Dict[str, Any]:
    """
    Loads raw Yaml file
    """
    file_path = BASE_DIR / f"{name}_{version}.yaml"

    if not file_path.exists():
        raise FileNotFoundError(f"Prompt template '{name}' with version '{version}' not found at {file_path}")
    
    with open(file_path, encoding="utf-8") as file:
        try:
            prompt_data = yaml.safe_load(file)
            return prompt_data
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file '{file_path}': {e}")
        
def format_prompt(name: str, variables: Dict[str, Any], version: str = "v1") -> Dict[str, str]:
    """
    1. Loads the prompt.
    2. Zips the variables into the template.
    3. Returns the final System and User messages.
    """

    data = get_prompt_template(name, version)

    system_role = data.get("role", "system")
    system_content = data.get('content', '')
    user_template = data.get("template", "")

    try:
#how we unpack dict in python, to get string from dict
        formatted_user_message = user_template.format(**variables)
    except KeyError as e:
        raise ValueError(f"Missing variable in prompt {name}: {e}")

    # 4. Return ready-to-use messages
    return {
        "system": system_content,
        "user": formatted_user_message
    }
