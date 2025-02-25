from PIL import Image
import numpy as np
import time
import threading
import mss
from typing import Optional, Tuple, List
import queue

class ScreenRecorder:
    def __init__(self, fps=30.0):
        """Initialize screen recorder with thread safety."""
        self.fps = fps
        self.recording = False
        self.frames = []
        self.frame_interval = 1.0 / fps
        self.selection_rect = None
        self.lock = threading.Lock()
        self._frame_times = []
        self.frame_queue = queue.Queue(maxsize=30)  # Buffer 30 frames
        
        # MSS instances will be created per-thread
        self.thread_local = threading.local()

    def get_screenshot(self):
        """Get thread-local MSS instance."""
        if not hasattr(self.thread_local, 'sct'):
            self.thread_local.sct = mss.mss()
        return self.thread_local.sct

    def capture_region(self, region: Optional[Tuple[int, int, int, int]] = None) -> Optional[Image.Image]:
        """Capture screen region using thread-local MSS instance."""
        try:
            sct = self.get_screenshot()
            monitor = {}
            
            if region:
                left, top, right, bottom = region
                monitor = {
                    "left": max(0, left),
                    "top": max(0, top),
                    "width": max(1, right - left),
                    "height": max(1, bottom - top)
                }
            else:
                monitor = sct.monitors[1]

            screenshot = sct.grab(monitor)
            if not screenshot:
                raise RuntimeError("Screenshot capture failed")
                
            return Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            
        except Exception as e:
            print(f"Screen capture error: {str(e)}")
            return None

    def _record_frames(self):
        """Main recording loop with thread-safe capture."""
        try:
            sct = self.get_screenshot()  # Get thread-local MSS instance
            next_frame_time = time.perf_counter()
            
            while self.recording:
                frame_start = time.perf_counter()
                
                # Capture frame
                frame = self.capture_region(self.selection_rect)
                if frame:
                    frame_array = np.array(frame)
                    
                    # Use queue to prevent memory issues
                    try:
                        self.frame_queue.put(frame_array, timeout=1)
                    except queue.Full:
                        # Remove oldest frame if queue is full
                        try:
                            self.frame_queue.get_nowait()
                            self.frame_queue.put(frame_array)
                        except queue.Empty:
                            pass
                
                # Timing control
                frame_duration = time.perf_counter() - frame_start
                sleep_time = max(0, self.frame_interval - frame_duration)
                next_frame_time += self.frame_interval
                time.sleep(sleep_time)
                
        except Exception as e:
            print(f"Recording error: {str(e)}")
        finally:
            if hasattr(self.thread_local, 'sct'):
                self.thread_local.sct.close()
                del self.thread_local.sct

    def start_recording(self, region=None):
        """Start screen recording thread."""
        if self.recording:
            return

        self.recording = True
        self.selection_rect = region
        
        # Clear queues and lists
        while not self.frame_queue.empty():
            self.frame_queue.get()
        with self.lock:
            self.frames.clear()
            self._frame_times.clear()

        self.record_thread = threading.Thread(
            target=self._record_frames,
            name="ScreenRecorder-Thread",
            daemon=True
        )
        self.record_thread.start()

    def stop_recording(self) -> List[np.ndarray]:
        """Safely stop recording and return captured frames."""
        self.recording = False
        
        if hasattr(self, 'record_thread') and self.record_thread.is_alive():
            self.record_thread.join(timeout=2.0)
        
        # Collect all frames from queue
        frames = []
        while not self.frame_queue.empty():
            frames.append(self.frame_queue.get())
            
        return frames

    def __del__(self):
        """Cleanup resources."""
        self.recording = False
        if hasattr(self, 'record_thread') and self.record_thread.is_alive():
            self.record_thread.join(timeout=1.0)