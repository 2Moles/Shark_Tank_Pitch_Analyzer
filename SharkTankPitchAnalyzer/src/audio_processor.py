"""Audio Processing Module - Vocal Feature Extraction using Librosa"""

import logging
from typing import Dict, Tuple, List, Any
from pathlib import Path
import numpy as np
import librosa
import soundfile as sf
from config import SAMPLE_RATE, N_MELS, N_FFT, HOP_LENGTH, AUDIO_DURATION_MIN, AUDIO_DURATION_MAX

logger = logging.getLogger(__name__)


class AudioProcessor:
    """
    Handles audio loading, preprocessing, and vocal feature extraction.
    Extracts pitch, pace, volume, and pauses using Librosa.
    """
    
    def __init__(self, sample_rate: int = SAMPLE_RATE):
        """Initialize audio processor"""
        self.sample_rate = sample_rate
        logger.info(f"AudioProcessor initialized with sample rate: {sample_rate}")
    
    def load_audio(self, audio_path: Path) -> Tuple[np.ndarray, int]:
        """
        Load audio file and resample to target sample rate
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Tuple of (audio_array, sample_rate)
        """
        try:
            logger.info(f"Loading audio from {audio_path}")
            y, sr = librosa.load(str(audio_path), sr=self.sample_rate)
            logger.info(f"Audio loaded successfully. Duration: {len(y) / sr:.2f}s")
            return y, sr
        except Exception as e:
            logger.error(f"Error loading audio: {e}")
            raise
    
    def validate_audio_duration(self, y: np.ndarray, sr: int) -> Tuple[bool, str]:
        """Validate audio duration is within acceptable range"""
        duration = len(y) / sr
        
        if duration < AUDIO_DURATION_MIN:
            return False, f"Audio too short: {duration:.1f}s (minimum: {AUDIO_DURATION_MIN}s)"
        
        if duration > AUDIO_DURATION_MAX:
            return False, f"Audio too long: {duration:.1f}s (maximum: {AUDIO_DURATION_MAX}s)"
        
        return True, f"Audio duration valid: {duration:.1f}s"
    
    def preprocess_audio(self, y: np.ndarray, sr: int) -> np.ndarray:
        """
        Preprocess audio: noise reduction and normalization
        
        Args:
            y: Audio time series
            sr: Sample rate
        
        Returns:
            Preprocessed audio
        """
        try:
            logger.info("Preprocessing audio...")
            
            # Normalize to -1 to 1
            y = y / (np.max(np.abs(y)) + 1e-8)
            
            # Apply pre-emphasis filter (enhance high frequencies)
            pre_emphasis = 0.97
            y = np.append(y[0], y[1:] - pre_emphasis * y[:-1])
            
            logger.info("Audio preprocessing complete")
            return y
        
        except Exception as e:
            logger.error(f"Error preprocessing audio: {e}")
            raise
    
    def extract_pitch(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """
        Extract pitch characteristics using Librosa
        
        Returns:
            Dictionary with pitch metrics
        """
        try:
            logger.info("Extracting pitch features...")
            
            # Extract fundamental frequency using pyin (probabilistic YIN)
            f0, voiced_flag, voiced_probs = librosa.pyin(
                y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'),
                sr=sr, hop_length=HOP_LENGTH
            )
            
            # Remove NaN values
            f0_valid = f0[~np.isnan(f0)]
            
            if len(f0_valid) == 0:
                return {
                    'mean_pitch_hz': 0,
                    'std_pitch_hz': 0,
                    'min_pitch_hz': 0,
                    'max_pitch_hz': 0,
                    'pitch_variety': 0,
                    'voiced_percentage': 0,
                }
            
            pitch_features = {
                'mean_pitch_hz': float(np.mean(f0_valid)),
                'std_pitch_hz': float(np.std(f0_valid)),
                'min_pitch_hz': float(np.min(f0_valid)),
                'max_pitch_hz': float(np.max(f0_valid)),
                'pitch_variety': float(np.std(f0_valid) / np.mean(f0_valid)) if np.mean(f0_valid) > 0 else 0,
                'voiced_percentage': float(np.sum(voiced_flag) / len(voiced_flag) * 100) if len(voiced_flag) > 0 else 0,
            }
            
            logger.info(f"Pitch features extracted: mean={pitch_features['mean_pitch_hz']:.1f}Hz")
            return pitch_features
        
        except Exception as e:
            logger.error(f"Error extracting pitch: {e}")
            return self._get_default_pitch_features()
    
    def extract_pace(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """
        Extract pace characteristics (speech rate, tempo variations)
        
        Returns:
            Dictionary with pace metrics
        """
        try:
            logger.info("Extracting pace features...")
            
            # Compute onset strength
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            
            # Compute tempo
            tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
            
            # Compute spectral centroid to get voice characteristics
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=HOP_LENGTH)[0]
            spectral_cent_mean = np.mean(spectral_centroids)
            spectral_cent_std = np.std(spectral_centroids)
            
            # Compute zero crossing rate (voice activity)
            zcr = librosa.feature.zero_crossing_rate(y, hop_length=HOP_LENGTH)[0]
            zcr_mean = np.mean(zcr)
            
            pace_features = {
                'tempo_bpm': float(tempo),
                'onset_count': len(beats),
                'spectral_centroid_mean': float(spectral_cent_mean),
                'spectral_centroid_std': float(spectral_cent_std),
                'zero_crossing_rate': float(zcr_mean),
            }
            
            logger.info(f"Pace features extracted: tempo={tempo:.1f}BPM")
            return pace_features
        
        except Exception as e:
            logger.error(f"Error extracting pace: {e}")
            return self._get_default_pace_features()
    
    def extract_volume(self, y: np.ndarray, sr: int) -> Dict[str, float]:
        """
        Extract volume and energy characteristics
        
        Returns:
            Dictionary with volume metrics
        """
        try:
            logger.info("Extracting volume features...")
            
            # Compute RMS energy
            rms = librosa.feature.rms(y=y, hop_length=HOP_LENGTH)[0]
            
            # Compute MFCC (Mel-frequency cepstral coefficients) for more detailed spectral info
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=HOP_LENGTH)
            
            # Compute mel spectrogram
            mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=N_MELS, hop_length=HOP_LENGTH)
            db_spec = librosa.power_to_db(mel_spec, ref=np.max)
            
            volume_features = {
                'rms_energy_mean': float(np.mean(rms)),
                'rms_energy_std': float(np.std(rms)),
                'rms_energy_max': float(np.max(rms)),
                'rms_energy_min': float(np.min(rms)),
                'dynamic_range': float(np.max(rms) - np.min(rms)),
                'mfcc_mean': float(np.mean(mfcc)),
                'mfcc_std': float(np.std(mfcc)),
                'spectral_energy_mean': float(np.mean(db_spec)),
                'spectral_energy_std': float(np.std(db_spec)),
            }
            
            logger.info(f"Volume features extracted: RMS mean={volume_features['rms_energy_mean']:.4f}")
            return volume_features
        
        except Exception as e:
            logger.error(f"Error extracting volume: {e}")
            return self._get_default_volume_features()
    
    def detect_pauses(self, y: np.ndarray, sr: int, threshold: float = 0.02) -> Dict[str, Any]:
        """
        Detect pauses and silence in speech
        
        Args:
            y: Audio time series
            sr: Sample rate
            threshold: Energy threshold for pause detection (0-1)
        
        Returns:
            Dictionary with pause characteristics
        """
        try:
            logger.info("Detecting pauses...")
            
            # Compute STFT magnitude
            D = librosa.stft(y, n_fft=N_FFT, hop_length=HOP_LENGTH)
            S = np.abs(D)
            
            # Sum across frequency bins to get temporal energy
            energy = np.sum(S, axis=0)
            
            # Normalize energy
            if np.max(energy) > 0:
                energy = energy / np.max(energy)
            
            # Detect pauses (low energy)
            pauses = energy < threshold
            
            # Find contiguous pause regions
            pause_frames = np.where(pauses)[0]
            
            if len(pause_frames) == 0:
                return self._get_default_pause_features()
            
            # Group consecutive frames
            pause_groups = []
            current_group = [pause_frames[0]]
            
            for frame in pause_frames[1:]:
                if frame == current_group[-1] + 1:
                    current_group.append(frame)
                else:
                    if len(current_group) > 1:  # Only count pauses of at least 2 frames
                        pause_groups.append(current_group)
                    current_group = [frame]
            
            if len(current_group) > 1:
                pause_groups.append(current_group)
            
            # Calculate pause statistics
            frame_length = HOP_LENGTH / sr
            pause_durations = [len(g) * frame_length for g in pause_groups]
            
            pause_features = {
                'pause_count': len(pause_groups),
                'avg_pause_duration': float(np.mean(pause_durations)) if pause_durations else 0,
                'max_pause_duration': float(np.max(pause_durations)) if pause_durations else 0,
                'min_pause_duration': float(np.min(pause_durations)) if pause_durations else 0,
                'total_pause_duration': float(np.sum(pause_durations)),
                'pause_frequency': len(pause_groups) / (len(y) / sr),  # pauses per second
            }
            
            logger.info(f"Pauses detected: {pause_features['pause_count']} pauses")
            return pause_features
        
        except Exception as e:
            logger.error(f"Error detecting pauses: {e}")
            return self._get_default_pause_features()
    
    def extract_all_vocal_features(self, audio_path: Path) -> Dict[str, Any]:
        """
        Extract all vocal features from audio file
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Dictionary containing all vocal features
        """
        try:
            # Load audio
            y, sr = self.load_audio(audio_path)
            
            # Validate duration
            is_valid, duration_msg = self.validate_audio_duration(y, sr)
            if not is_valid:
                logger.warning(duration_msg)
            
            # Preprocess
            y = self.preprocess_audio(y, sr)
            
            # Extract features
            pitch_features = self.extract_pitch(y, sr)
            pace_features = self.extract_pace(y, sr)
            volume_features = self.extract_volume(y, sr)
            pause_features = self.detect_pauses(y, sr)
            
            # Combine all features
            all_features = {
                'pitch': pitch_features,
                'pace': pace_features,
                'volume': volume_features,
                'pauses': pause_features,
                'duration_seconds': float(len(y) / sr),
                'sample_rate': sr,
            }
            
            logger.info("All vocal features extracted successfully")
            return all_features
        
        except Exception as e:
            logger.error(f"Error extracting vocal features: {e}")
            raise
    
    @staticmethod
    def _get_default_pitch_features() -> Dict[str, float]:
        """Return default pitch features when extraction fails"""
        return {
            'mean_pitch_hz': 0,
            'std_pitch_hz': 0,
            'min_pitch_hz': 0,
            'max_pitch_hz': 0,
            'pitch_variety': 0,
            'voiced_percentage': 0,
        }
    
    @staticmethod
    def _get_default_pace_features() -> Dict[str, float]:
        """Return default pace features when extraction fails"""
        return {
            'tempo_bpm': 0,
            'onset_count': 0,
            'spectral_centroid_mean': 0,
            'spectral_centroid_std': 0,
            'zero_crossing_rate': 0,
        }
    
    @staticmethod
    def _get_default_volume_features() -> Dict[str, float]:
        """Return default volume features when extraction fails"""
        return {
            'rms_energy_mean': 0,
            'rms_energy_std': 0,
            'rms_energy_max': 0,
            'rms_energy_min': 0,
            'dynamic_range': 0,
            'mfcc_mean': 0,
            'mfcc_std': 0,
            'spectral_energy_mean': 0,
            'spectral_energy_std': 0,
        }
    
    @staticmethod
    def _get_default_pause_features() -> Dict[str, Any]:
        """Return default pause features when detection fails"""
        return {
            'pause_count': 0,
            'avg_pause_duration': 0,
            'max_pause_duration': 0,
            'min_pause_duration': 0,
            'total_pause_duration': 0,
            'pause_frequency': 0,
        }
