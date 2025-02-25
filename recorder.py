from screen_capture import ScreenRecorder
from audio_capture import AudioRecorder
from video_processing import VideoProcessor
from utils.file_utils import generate_filename
import threading
import time
import os
from typing import Tuple, Optional

class Recorder:
    def __init__(self, fps=30.0, sample_rate=44100):
        """Initialize the recorder with both screen and audio capabilities.
        
        Args:
            fps: Frames per second for video
            sample_rate: Sample rate for audio in Hz
        """
        self.screen_recorder = ScreenRecorder(fps=fps)
        self.audio_recorder = AudioRecorder(sample_rate=sample_rate)
        self.video_processor = VideoProcessor(fps=fps)
        self.recording = False
        self.frames = []
        self.audio_data = None
        
    def start_recording(self, region=None, record_audio=True):  # Add record_audio parameter
        """Start recording screen.
        
        Args:
            region: Custom region to record (left, top, right, bottom)
            record_audio: Whether to record audio (from GUI checkbox)
        """
        if self.recording:
            return
            
        self.recording = True
        self.frames = []

        # Start screen recording
        self.screen_recorder.start_recording(region=region)
        
        # Start audio recording only if enabled
        if record_audio:
            self.audio_recorder.start_recording()
        
    def stop_recording(self):
        """Stop recording and save the video file.
        
        Returns:
            Path to the saved video file
        """
        if not self.recording:
            return None
            
        self.recording = False
        
        # Stop screen recording and get frames
        frames = self.screen_recorder.stop_recording()
        
        # Stop audio recording if active
        audio_data = None
        if hasattr(self, 'audio_recorder') and self.audio_recorder:
            audio_data = self.audio_recorder.stop_recording()
        
        # Store the captured data
        self.frames = frames
        self.audio_data = audio_data
        
        # Save the recording
        return self.save_recording()
        
    def save_recording(self):
        """Save the recording to file.
        
        Returns:
            Path to the saved video file
        """
        if not self.frames:
            return None
            
        # Generate output paths
        video_path = generate_filename(prefix="recording", extension="mp4")
        audio_path = None
        
        # Save audio if we have it
        if self.audio_data is not None:
            audio_path = generate_filename(prefix="audio", extension="wav")
            self.audio_recorder.save_audio(self.audio_data, audio_path)
        
        # Create and save video
        self.video_processor.output_path = video_path
        try:
            result_path = self.video_processor.frames_to_video(self.frames, audio_path)
            
            # Clean up the temporary audio file
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
                
            return result_path
        except Exception as e:
            print(f"Error saving recording: {e}")
            return None
        
    def add_annotation(self, text: str, position: Tuple[int, int], **kwargs):
        """Add a text annotation to the video.
        
        Args:
            text: Text to display
            position: (x, y) position for the text
            **kwargs: Additional annotation parameters
        """
        self.video_processor.add_annotation(text, position, **kwargs)
        
    def remove_annotation(self, index: int):
        """Remove an annotation by index."""
        self.video_processor.remove_annotation(index)
        
    def clear_annotations(self):
        """Remove all annotations."""
        self.video_processor.clear_annotations()
