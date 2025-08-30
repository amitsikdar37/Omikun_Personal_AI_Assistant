
from faster_whisper import WhisperModel
import numpy as np

class STT:
    def __init__(self):
        # Load small model for speed (change to "medium" for better accuracy)
        self.model = WhisperModel("medium", device="cpu", compute_type="int8")
        print("STT initialized")
    
    def transcribe(self, audio_data, sample_rate=16000):
        """Convert audio to text"""
        try:
            # Convert to numpy array if needed
            if not isinstance(audio_data, np.ndarray):
                audio_data = np.array(audio_data, dtype=np.float32)
            
            # Transcribe
            segments, info = self.model.transcribe(audio_data, beam_size=5)
            
            # Get text from segments
            text = ""
            for segment in segments:
                text += segment.text + " "
            
            return text.strip()
        except Exception as e:
            print(f"STT Error: {e}")
            return ""
