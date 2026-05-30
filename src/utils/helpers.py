import json
from typing import Dict, Any
from src.utils.logger import logger

def clean_and_parse_json(content: str) -> Dict[str, Any]:
    """
    Cleans markdown wrappers like ```json and parses a JSON string.
    """
    cleaned = (
        content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response. Content: {cleaned[:500]}... Error: {str(e)}")
        raise e
