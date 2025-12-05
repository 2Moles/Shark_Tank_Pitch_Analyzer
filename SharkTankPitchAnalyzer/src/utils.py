"""Utility functions for Shark Tank Pitch Analyzer"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
import numpy as np
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def save_results(results: Dict[str, Any], output_path: Path) -> None:
    """Save analysis results to JSON file"""
    try:
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Results saved to {output_path}")
    except Exception as e:
        logger.error(f"Error saving results: {e}")
        raise


def load_results(input_path: Path) -> Dict[str, Any]:
    """Load analysis results from JSON file"""
    try:
        with open(input_path, 'r') as f:
            results = json.load(f)
        logger.info(f"Results loaded from {input_path}")
        return results
    except Exception as e:
        logger.error(f"Error loading results: {e}")
        raise


def normalize_score(score: float, min_val: float = 0, max_val: float = 10) -> float:
    """Normalize a score to 0-10 scale"""
    if max_val == min_val:
        return 5.0
    normalized = ((score - min_val) / (max_val - min_val)) * 10
    return max(0, min(10, normalized))


def calculate_weighted_average(scores: Dict[str, float], weights: Dict[str, float]) -> float:
    """Calculate weighted average of scores"""
    total_weight = sum(weights.values())
    if total_weight == 0:
        return 0.0
    
    weighted_sum = sum(scores.get(key, 0) * weight for key, weight in weights.items())
    return weighted_sum / total_weight


def get_verdict_category(score: float) -> str:
    """Get verdict category based on score"""
    if score >= 7.0:
        return "Invest"
    elif score >= 5.0:
        return "Need More Info"
    else:
        return "Not Invest"


def format_timestamp() -> str:
    """Get current timestamp in standard format"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def validate_audio_file(file_path: Path, max_duration: int = 600) -> Tuple[bool, str]:
    """
    Validate audio file format and duration
    
    Args:
        file_path: Path to audio file
        max_duration: Maximum allowed duration in seconds
    
    Returns:
        Tuple of (is_valid, message)
    """
    try:
        import librosa
        
        if not file_path.exists():
            return False, "File does not exist"
        
        # Check file extension
        valid_extensions = {'.wav', '.mp3', '.m4a', '.flac', '.ogg'}
        if file_path.suffix.lower() not in valid_extensions:
            return False, f"Unsupported audio format. Supported: {valid_extensions}"
        
        # Check duration
        y, sr = librosa.load(file_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)
        
        if duration < 30:
            return False, "Audio must be at least 30 seconds long"
        
        if duration > max_duration:
            return False, f"Audio must be less than {max_duration} seconds"
        
        return True, f"Valid audio file ({duration:.1f} seconds)"
    
    except Exception as e:
        return False, f"Error validating audio: {str(e)}"


def extract_keywords(text: str, n: int = 10) -> List[str]:
    """Extract top keywords from text using TF-IDF"""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        vectorizer = TfidfVectorizer(max_features=n, stop_words='english')
        vectorizer.fit_transform([text])
        return vectorizer.get_feature_names_out().tolist()
    
    except Exception as e:
        logger.error(f"Error extracting keywords: {e}")
        return []


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def create_summary(pitch_data: Dict[str, Any]) -> str:
    """Create a one-line summary of the pitch"""
    transcript = pitch_data.get('transcript', '')
    if len(transcript) > 200:
        return transcript[:200] + "..."
    return transcript


class AudioMetrics:
    """Helper class for audio metrics calculations"""
    
    @staticmethod
    def calculate_speech_rate(transcript: str, duration_seconds: float) -> float:
        """Calculate words per minute"""
        words = len(transcript.split())
        minutes = duration_seconds / 60
        if minutes == 0:
            return 0
        return words / minutes
    
    @staticmethod
    def detect_pauses(audio_array: np.ndarray, sr: int, threshold: float = 0.02) -> Tuple[int, float]:
        """
        Detect pauses in audio
        
        Returns:
            Tuple of (pause_count, average_pause_duration)
        """
        import librosa
        
        # Compute energy
        S = librosa.feature.melspectrogram(y=audio_array, sr=sr)
        log_S = librosa.power_to_db(S, ref=np.max)
        energy = np.mean(log_S, axis=0)
        
        # Normalize energy
        energy = (energy - np.min(energy)) / (np.max(energy) - np.min(energy))
        
        # Detect pauses (low energy regions)
        pauses = energy < threshold
        pause_frames = np.where(pauses)[0]
        
        if len(pause_frames) == 0:
            return 0, 0.0
        
        # Group consecutive pause frames
        pause_groups = []
        current_group = [pause_frames[0]]
        
        for frame in pause_frames[1:]:
            if frame == current_group[-1] + 1:
                current_group.append(frame)
            else:
                pause_groups.append(current_group)
                current_group = [frame]
        
        pause_groups.append(current_group)
        
        # Calculate statistics
        pause_count = len(pause_groups)
        hop_length = 512
        frame_duration = hop_length / sr
        avg_pause_duration = np.mean([len(g) * frame_duration for g in pause_groups])
        
        return pause_count, avg_pause_duration


def setup_spacy_model(model_name: str = "en_core_web_sm") -> Any:
    """Load spaCy model with automatic download if needed"""
    try:
        import spacy
        try:
            nlp = spacy.load(model_name)
        except OSError:
            logger.info(f"Downloading spaCy model {model_name}...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", model_name], check=True)
            nlp = spacy.load(model_name)
        return nlp
    except Exception as e:
        logger.error(f"Error loading spaCy model: {e}")
        return None
