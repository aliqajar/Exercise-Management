from enum import Enum
from uuid import UUID
from typing import Optional

class InteractionType(str, Enum):
    FAVORITE = "favorites"
    SAVE = "saves"

def is_valid_uuid(uuid_str: str) -> bool:
    """Check if a string is a valid UUID"""
    try:
        UUID(uuid_str)
        return True
    except ValueError:
        return False

def validate_interaction_type(interaction_type: str) -> Optional[str]:
    """Validate interaction type and return normalized value"""
    try:
        return InteractionType(interaction_type.lower())
    except ValueError:
        return None 