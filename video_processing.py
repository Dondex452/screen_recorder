import cv2
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip, ImageSequenceClip
from pathlib import Path
import tempfile
import os
from annotations import AnnotationManager
from typing import List, Optional

class VideoProcessor:
    def __init__(self, output_path=None, fps=30.0):
        """Initialize video processor.
        
        Args:
            output_path: Path to save the video
            fps: Frames per second for the output video
        """
        self.output_path = output_path
        self.fps = fps
        self.temp_dir = tempfile.mkdtemp()
        self.annotation_manager = AnnotationManager()
        
    def frames_to_video(self, frames: List[np.ndarray], audio_path: Optional[str] = None):
        """Convert frames to video file.
        
        Args:
            frames: List of numpy arrays containing frame data
            audio_path: Optional path to audio file to merge with video
        
        Returns:
            Path to the created video file
        """
        if not frames:
            raise ValueError("No frames provided for video creation")
            
        try:
            # Apply annotations to frames
            annotated_frames = []
            for frame in frames:
                annotated_frame = self.annotation_manager.draw_annotations(frame.copy())
                annotated_frames.append(annotated_frame)
                
            # Create video from frames
            clip = ImageSequenceClip(annotated_frames, fps=self.fps)
            
            # Add audio if provided
            if audio_path and os.path.exists(audio_path):
                audio = AudioFileClip(audio_path)
                clip = clip.set_audio(audio)
            
            # Save video with proper error handling
            try:
                clip.write_videofile(
                    self.output_path,
                    codec='libx264',
                    audio_codec='aac' if audio_path else None,
                    temp_audiofile=os.path.join(self.temp_dir, "temp-audio.m4a"),
                    remove_temp=True,
                    threads=4
                )
            finally:
                clip.close()
                if audio_path and os.path.exists(audio_path):
                    try:
                        os.remove(audio_path)
                    except:
                        pass
            
            return self.output_path
            
        except Exception as e:
            raise RuntimeError(f"Failed to create video: {str(e)}")
        
    def trim_video(self, start_time: float, end_time: float):
        """Trim video to specified time range.
        
        Args:
            start_time: Start time in seconds
            end_time: End time in seconds
        """
        if not self.output_path or not os.path.exists(self.output_path):
            raise ValueError("No video file to trim")
            
        clip = VideoFileClip(self.output_path)
        trimmed = clip.subclip(start_time, end_time)
        
        # Create new filename for trimmed video
        path = Path(self.output_path)
        trimmed_path = str(path.parent / f"{path.stem}_trimmed{path.suffix}")
        
        trimmed.write_videofile(trimmed_path, 
                              codec='libx264',
                              audio_codec='aac' if clip.audio else None)
        
        clip.close()
        trimmed.close()
        
        # Update output path to trimmed video
        self.output_path = trimmed_path
        return self.output_path
        
    def add_annotation(self, text: str, position: tuple, **kwargs):
        """Add a text annotation to the video.
        
        Args:
            text: Text to display
            position: (x, y) position for the text
            **kwargs: Additional annotation parameters (color, font_scale, etc.)
        """
        self.annotation_manager.add_annotation(text, position, **kwargs)
        
    def remove_annotation(self, index: int):
        """Remove an annotation by index."""
        self.annotation_manager.remove_annotation(index)
        
    def clear_annotations(self):
        """Remove all annotations."""
        self.annotation_manager.clear_annotations()
