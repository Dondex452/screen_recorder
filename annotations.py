import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional
import time

@dataclass
class TextAnnotation:
    """Class to store text annotation data."""
    text: str
    position: Tuple[int, int]
    color: Tuple[int, int, int] = (255, 255, 255)  # Default: white
    font_scale: float = 1.0
    thickness: int = 2
    font_face: int = cv2.FONT_HERSHEY_SIMPLEX
    background_color: Optional[Tuple[int, int, int]] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class AnnotationManager:
    def __init__(self):
        """Initialize the annotation manager."""
        self.annotations: List[TextAnnotation] = []
        self.current_annotation = None
        
    def add_annotation(self, text: str, position: Tuple[int, int], 
                      color: Tuple[int, int, int] = (255, 255, 255),
                      font_scale: float = 1.0, thickness: int = 2,
                      background_color: Optional[Tuple[int, int, int]] = None):
        """Add a new text annotation.
        
        Args:
            text: Text to display
            position: (x, y) position for the text
            color: RGB color tuple for the text
            font_scale: Scale factor for the font
            thickness: Thickness of the text
            background_color: Optional RGB color tuple for text background
        """
        annotation = TextAnnotation(
            text=text,
            position=position,
            color=color,
            font_scale=font_scale,
            thickness=thickness,
            background_color=background_color
        )
        self.annotations.append(annotation)
        
    def remove_annotation(self, index: int):
        """Remove an annotation by index."""
        if 0 <= index < len(self.annotations):
            self.annotations.pop(index)
            
    def clear_annotations(self):
        """Remove all annotations."""
        self.annotations.clear()
        
    def draw_annotations(self, frame: np.ndarray) -> np.ndarray:
        """Draw all annotations on a frame.
        
        Args:
            frame: Input frame to draw on
            
        Returns:
            Frame with annotations drawn
        """
        annotated_frame = frame.copy()
        
        for annotation in self.annotations:
            # Get text size for background rectangle if needed
            (text_width, text_height), baseline = cv2.getTextSize(
                annotation.text,
                annotation.font_face,
                annotation.font_scale,
                annotation.thickness
            )
            
            # Draw background rectangle if color specified
            if annotation.background_color is not None:
                x, y = annotation.position
                cv2.rectangle(
                    annotated_frame,
                    (x, y - text_height - baseline),
                    (x + text_width, y + baseline),
                    annotation.background_color,
                    -1  # Fill rectangle
                )
            
            # Draw text
            cv2.putText(
                annotated_frame,
                annotation.text,
                annotation.position,
                annotation.font_face,
                annotation.font_scale,
                annotation.color,
                annotation.thickness,
                cv2.LINE_AA
            )
            
        return annotated_frame
        
    def get_annotation_at_position(self, position: Tuple[int, int], 
                                 frame_size: Tuple[int, int]) -> Optional[int]:
        """Get the index of an annotation at the given position.
        
        Args:
            position: (x, y) position to check
            frame_size: (width, height) of the frame
            
        Returns:
            Index of the annotation if found, None otherwise
        """
        x, y = position
        frame_width, frame_height = frame_size
        
        for i, annotation in enumerate(self.annotations):
            # Get text size
            (text_width, text_height), baseline = cv2.getTextSize(
                annotation.text,
                annotation.font_face,
                annotation.font_scale,
                annotation.thickness
            )
            
            # Calculate text bounds
            ax, ay = annotation.position
            text_bounds = (
                ax,
                ay - text_height - baseline,
                ax + text_width,
                ay + baseline
            )
            
            # Check if position is within bounds
            if (text_bounds[0] <= x <= text_bounds[2] and
                text_bounds[1] <= y <= text_bounds[3]):
                return i
                
        return None
