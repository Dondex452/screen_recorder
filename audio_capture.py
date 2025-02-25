import sounddevice as sd
import numpy as np
import wave
import tempfile
import os
from threading import Lock

class AudioRecorder:
    def __init__(self, sample_rate=44100):
        """Initialize audio recorder.
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.recording = False
        self.audio_data = []
        self.stream = None
        self.audio_lock = Lock()
        self.temp_dir = tempfile.mkdtemp()
        
    def start_recording(self, channels=2):
        """Start audio recording.
        
        Args:
            channels: Number of audio channels (1 for mono, 2 for stereo)
        """
        if self.recording:
            return
            
        self.recording = True
        self.audio_data = []
        
        def callback(indata, frames, time, status):
            if status:
                print(f'Audio recording error: {status}')
            if self.recording:
                with self.audio_lock:
                    self.audio_data.append(indata.copy())
        
        try:
            # Test audio device availability first
            devices = sd.query_devices()
            if not any(device['max_input_channels'] > 0 for device in devices):
                raise RuntimeError("No audio input devices found")

            self.stream = sd.InputStream(
                channels=channels,
                samplerate=self.sample_rate,
                callback=callback,
                blocksize=2048,  # Optimize buffer size
                latency='low'    # Reduce latency
            )
            self.stream.start()
        except Exception as e:
            self.recording = False
            raise RuntimeError(f"Audio recording error: {str(e)}")
        
    def stop_recording(self):
        """Stop audio recording and return the recorded audio data."""
        self.recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        with self.audio_lock:
            if self.audio_data:
                return np.concatenate(self.audio_data, axis=0)
        return None
        
    def save_audio(self, audio_data, output_path):
        """Save recorded audio to a WAV file.
        
        Args:
            audio_data: Numpy array of audio data
            output_path: Path to save the audio file
        
        Returns:
            Path to the saved audio file
        """
        if audio_data is None:
            return None
            
        temp_path = os.path.join(self.temp_dir, "temp_audio.wav")
        
        with wave.open(temp_path, 'wb') as wf:
            wf.setnchannels(2)  # Stereo
            wf.setsampwidth(2)  # 2 bytes per sample
            wf.setframerate(self.sample_rate)
            wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())
        
        # If output_path is provided, copy the temp file there
        if output_path:
            os.replace(temp_path, output_path)
            return output_path
        return temp_path
        
    def get_available_devices(self):
        """Get list of available audio input devices."""
        return sd.query_devices()
