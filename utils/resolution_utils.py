from typing import Tuple, Dict

RESOLUTIONS = {
    "480p": (854, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
}

def get_resolution_options() -> Dict[str, Tuple[int, int]]:
    """Get available resolution options."""
    return RESOLUTIONS

def calculate_aspect_ratio(width: int, height: int) -> float:
    """Calculate aspect ratio for given dimensions."""
    return width / height

def resize_dimensions(current_width: int, current_height: int, target_height: int) -> Tuple[int, int]:
    """Calculate new dimensions maintaining aspect ratio."""
    aspect_ratio = calculate_aspect_ratio(current_width, current_height)
    new_width = int(target_height * aspect_ratio)
    return new_width, target_height
