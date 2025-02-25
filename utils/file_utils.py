import os
from pathlib import Path

def get_default_save_directory():
    """Get the default directory for saving recordings."""
    videos_dir = str(Path.home() / "Videos" / "Screen Recordings")
    os.makedirs(videos_dir, exist_ok=True)
    return videos_dir

def generate_filename(prefix="recording", extension="mp4"):
    """Generate a unique filename for the recording."""
    base_dir = get_default_save_directory()
    counter = 1
    while True:
        filename = f"{prefix}_{counter}.{extension}"
        filepath = os.path.join(base_dir, filename)
        if not os.path.exists(filepath):
            return filepath
        counter += 1
