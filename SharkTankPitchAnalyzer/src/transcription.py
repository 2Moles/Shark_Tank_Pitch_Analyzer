"""Speech-to-Text Transcription Module using OpenAI Whisper"""

import logging
from pathlib import Path
from typing import Dict, Tuple
import whisper
from config import WHISPER_MODEL, WHISPER_DEVICE

logger = logging.getLogger(__name__)


class TranscriptionEngine:
    """
    Handles speech-to-text transcription using OpenAI Whisper.
    Supports various audio formats and provides detailed transcription data.
    """
    
    def __init__(self, model_name: str = WHISPER_MODEL, device: str = WHISPER_DEVICE):
        """
        Initialize transcription engine
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
            device: Device to use (cuda, cpu)
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load Whisper model"""
        try:
            logger.info(f"Loading Whisper model: {self.model_name} on device: {self.device}")
            self.model = whisper.load_model(self.model_name, device=self.device)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            # Fallback to CPU if CUDA fails
            if self.device == "cuda":
                logger.warning("Falling back to CPU")
                self.model = whisper.load_model(self.model_name, device="cpu")
            else:
                raise
    
    def transcribe(self, audio_path: Path, language: str = "en") -> Dict:
        """
        Transcribe audio file to text
        
        Args:
            audio_path: Path to audio file
            language: Language code (e.g., 'en' for English)
        
        Returns:
            Dictionary containing transcription results
        """
        try:
            if not self.model:
                raise RuntimeError("Model not loaded")
            
            logger.info(f"Transcribing audio from {audio_path}")
            
            result = self.model.transcribe(
                str(audio_path),
                language=language,
                verbose=False,
                temperature=0.0,  # More accurate
                best_of=5,  # Improve accuracy
            )
            
            return self._process_result(result)
        
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            raise
    
    def _process_result(self, result: Dict) -> Dict:
        """
        Process Whisper transcription result
        
        Args:
            result: Raw result from Whisper
        
        Returns:
            Processed transcription data
        """
        try:
            # Extract main transcript
            full_transcript = result.get("text", "").strip()
            
            # Extract segments with timestamps
            segments = []
            for segment in result.get("segments", []):
                segments.append({
                    "id": segment.get("id"),
                    "start_time": segment.get("start"),
                    "end_time": segment.get("end"),
                    "text": segment.get("text", "").strip(),
                    "confidence": segment.get("confidence", 0),
                })
            
            # Calculate statistics
            word_count = len(full_transcript.split())
            duration = result.get("result", {}).get("duration", 0)
            if duration == 0 and segments:
                duration = segments[-1].get("end_time", 0)
            
            processed = {
                "full_transcript": full_transcript,
                "segments": segments,
                "language": result.get("language", "unknown"),
                "duration_seconds": float(duration) if duration else 0,
                "word_count": word_count,
                "sentences": full_transcript.split('. '),
                "confidence": result.get("result", {}).get("avg_logprob", 0),
            }
            
            logger.info(f"Transcription processed: {word_count} words, {len(segments)} segments")
            return processed
        
        except Exception as e:
            logger.error(f"Error processing transcription result: {e}")
            raise
    
    def get_word_timings(self, audio_path: Path) -> Dict[str, Tuple[float, float]]:
        """
        Get word-level timing information
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Dictionary mapping words to (start_time, end_time) tuples
        """
        try:
            result = self.model.transcribe(str(audio_path), language="en", word_level=True)
            
            word_timings = {}
            for segment in result.get("segments", []):
                words = segment.get("text", "").split()
                start_time = segment.get("start", 0)
                end_time = segment.get("end", 0)
                segment_duration = end_time - start_time
                
                if len(words) > 0:
                    word_duration = segment_duration / len(words)
                    current_time = start_time
                    
                    for word in words:
                        word_timings[word] = (current_time, current_time + word_duration)
                        current_time += word_duration
            
            return word_timings
        
        except Exception as e:
            logger.error(f"Error getting word timings: {e}")
            return {}


def create_transcription_engine(
    model_name: str = WHISPER_MODEL,
    device: str = WHISPER_DEVICE
) -> TranscriptionEngine:
    """Factory function to create transcription engine"""
    return TranscriptionEngine(model_name=model_name, device=device)
