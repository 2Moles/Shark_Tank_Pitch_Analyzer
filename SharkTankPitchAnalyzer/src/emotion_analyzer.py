"""Emotion Detection Module using openSMILE and Transformers"""

import logging
from pathlib import Path
from typing import Dict, List, Any
import numpy as np
from transformers import pipeline
import subprocess
import json
import tempfile

logger = logging.getLogger(__name__)


class EmotionAnalyzer:
    """
    Detects emotions from audio using openSMILE and Hugging Face transformers.
    Analyzes both acoustic features and transcribed text for emotional tone.
    """
    
    def __init__(self):
        """Initialize emotion analyzer"""
        self.audio_emotions = None
        self.text_emotion_pipeline = None
        self._initialize_models()
    
    def _initialize_models(self) -> None:
        """Initialize emotion detection models"""
        try:
            logger.info("Initializing emotion detection models...")
            
            # Load text-based emotion detection model
            self.text_emotion_pipeline = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                device=0 if self._has_cuda() else -1
            )
            
            logger.info("Emotion detection models initialized successfully")
        
        except Exception as e:
            logger.error(f"Error initializing emotion models: {e}")
            self.text_emotion_pipeline = None
    
    @staticmethod
    def _has_cuda() -> bool:
        """Check if CUDA is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False
    
    def extract_audio_emotions_opensmile(self, audio_path: Path) -> Dict[str, Any]:
        """
        Extract emotion-related features from audio using openSMILE
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Dictionary with emotional features
        """
        try:
            logger.info(f"Extracting audio emotions from {audio_path} using openSMILE...")
            
            # Try to use openSMILE if available
            try:
                import opensmile
                
                # Extract features using openSMILE (GeMAPS features good for emotion)
                smile = opensmile.Smile(
                    feature_set=opensmile.FeatureSet.eGeMAPSv02,
                    feature_level=opensmile.FeatureLevel.Functionals,
                )
                
                features_df = smile.process_file(str(audio_path))
                
                # Extract emotion-relevant acoustic features
                audio_emotions = {
                    'loudness_mean': float(features_df.get('Loudness_sma3', [0]).mean()) if 'Loudness_sma3' in features_df else 0,
                    'energy_mean': float(features_df.get('F0semitoneFrom27.5Hz_sma3nz', [0]).mean()) if 'F0semitoneFrom27.5Hz_sma3nz' in features_df else 0,
                    'jitter': float(features_df.get('jitterLocal_sma3nz', [0]).mean()) if 'jitterLocal_sma3nz' in features_df else 0,
                    'shimmer': float(features_df.get('shimmerLocaldB_sma3nz', [0]).mean()) if 'shimmerLocaldB_sma3nz' in features_df else 0,
                }
                
                logger.info("Audio emotions extracted using openSMILE")
                return audio_emotions
            
            except ImportError:
                logger.warning("openSMILE not available, using acoustic features fallback")
                return self._extract_audio_emotions_fallback(audio_path)
        
        except Exception as e:
            logger.error(f"Error extracting audio emotions: {e}")
            return self._get_default_audio_emotions()
    
    def _extract_audio_emotions_fallback(self, audio_path: Path) -> Dict[str, Any]:
        """
        Fallback emotion extraction using Librosa acoustic features
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Dictionary with acoustic emotional indicators
        """
        try:
            import librosa
            
            y, sr = librosa.load(str(audio_path), sr=16000)
            
            # Extract acoustic features that correlate with emotion
            # High energy/loudness can indicate excitement or anger
            rms_energy = librosa.feature.rms(y=y)[0]
            
            # Spectral features (brightness can indicate different emotions)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            
            # Zero crossing rate (related to consonants, fricatives)
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            
            # MFCC features (general voice characteristics)
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # Pitch variation (using onset strength as proxy)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            
            audio_emotions = {
                'energy_mean': float(np.mean(rms_energy)),
                'energy_std': float(np.std(rms_energy)),
                'spectral_brightness': float(np.mean(spectral_centroids)),
                'voice_quality': float(np.mean(zcr)),
                'mfcc_mean': float(np.mean(mfcc)),
                'mfcc_std': float(np.std(mfcc)),
                'pitch_variation': float(np.std(onset_env)),
            }
            
            logger.info("Audio emotions extracted using Librosa fallback")
            return audio_emotions
        
        except Exception as e:
            logger.error(f"Error in fallback emotion extraction: {e}")
            return self._get_default_audio_emotions()
    
    def detect_text_emotions(self, text: str) -> Dict[str, Any]:
        """
        Detect emotion from transcribed text using Hugging Face transformers
        
        Args:
            text: Transcribed speech text
        
        Returns:
            Dictionary with emotion classification and scores
        """
        try:
            if not self.text_emotion_pipeline:
                logger.warning("Text emotion pipeline not available")
                return self._get_default_text_emotions()
            
            logger.info(f"Analyzing text emotions (length: {len(text)} chars)...")
            
            # Split text into sentences for more granular analysis
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            
            if not sentences:
                return self._get_default_text_emotions()
            
            emotion_results = []
            
            # Analyze each sentence (limit to avoid token overflow)
            for sentence in sentences[:20]:  # Limit to first 20 sentences
                if len(sentence.split()) < 300:  # Limit to reasonable length
                    try:
                        result = self.text_emotion_pipeline(sentence)[0]
                        emotion_results.append({
                            'text': sentence[:100],
                            'emotion': result['label'],
                            'score': result['score'],
                        })
                    except Exception as e:
                        logger.debug(f"Error analyzing sentence: {e}")
                        continue
            
            if not emotion_results:
                return self._get_default_text_emotions()
            
            # Aggregate emotions
            emotion_counts = {}
            for result in emotion_results:
                emotion = result['emotion']
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + result['score']
            
            # Normalize
            total_score = sum(emotion_counts.values())
            emotion_distribution = {
                emotion: score / total_score
                for emotion, score in emotion_counts.items()
            }
            
            # Find dominant emotion
            dominant_emotion = max(emotion_distribution.items(), key=lambda x: x[1])
            
            text_emotions = {
                'dominant_emotion': dominant_emotion[0],
                'dominant_emotion_score': float(dominant_emotion[1]),
                'emotion_distribution': emotion_distribution,
                'analyzed_sentences': len(emotion_results),
            }
            
            logger.info(f"Text emotion detected: {text_emotions['dominant_emotion']}")
            return text_emotions
        
        except Exception as e:
            logger.error(f"Error detecting text emotions: {e}")
            return self._get_default_text_emotions()
    
    def analyze_emotional_tone(self, audio_path: Path, transcript: str) -> Dict[str, Any]:
        """
        Comprehensive emotional analysis combining audio and text
        
        Args:
            audio_path: Path to audio file
            transcript: Transcribed text
        
        Returns:
            Dictionary with combined emotional analysis
        """
        try:
            logger.info("Starting comprehensive emotional analysis...")
            
            # Extract audio emotions
            audio_emotions = self.extract_audio_emotions_opensmile(audio_path)
            
            # Detect text emotions
            text_emotions = self.detect_text_emotions(transcript)
            
            # Combine analysis
            combined_analysis = {
                'audio_emotions': audio_emotions,
                'text_emotions': text_emotions,
                'overall_emotional_state': self._infer_emotional_state(audio_emotions, text_emotions),
            }
            
            logger.info("Emotional analysis complete")
            return combined_analysis
        
        except Exception as e:
            logger.error(f"Error in emotional analysis: {e}")
            return self._get_default_combined_emotions()
    
    def _infer_emotional_state(self, audio_emotions: Dict, text_emotions: Dict) -> Dict[str, Any]:
        """
        Infer overall emotional state from combined signals
        
        Args:
            audio_emotions: Audio-based emotional features
            text_emotions: Text-based emotion classification
        
        Returns:
            Inferred emotional state
        """
        try:
            # Audio energy indicator
            energy_level = audio_emotions.get('energy_mean', 0)
            energy_normalized = min(energy_level * 10, 10) if energy_level > 0 else 0
            
            # Text emotion mapping to confidence/passion
            emotion_confidence_map = {
                'joy': 0.8,
                'anger': 0.7,
                'excitement': 0.85,
                'sadness': 0.3,
                'fear': 0.4,
                'surprise': 0.75,
                'disgust': 0.2,
                'neutral': 0.5,
            }
            
            dominant_emotion = text_emotions.get('dominant_emotion', 'neutral')
            text_confidence = emotion_confidence_map.get(dominant_emotion, 0.5)
            
            return {
                'emotional_intensity': energy_normalized,
                'emotional_confidence': text_confidence * 10,
                'emotional_alignment': 'strong' if abs(energy_normalized - (text_confidence * 10)) < 3 else 'mixed',
            }
        
        except Exception as e:
            logger.error(f"Error inferring emotional state: {e}")
            return {
                'emotional_intensity': 5.0,
                'emotional_confidence': 5.0,
                'emotional_alignment': 'unknown',
            }
    
    @staticmethod
    def _get_default_audio_emotions() -> Dict[str, Any]:
        """Return default audio emotions"""
        return {
            'energy_mean': 0,
            'energy_std': 0,
            'spectral_brightness': 0,
            'voice_quality': 0,
            'mfcc_mean': 0,
            'mfcc_std': 0,
            'pitch_variation': 0,
        }
    
    @staticmethod
    def _get_default_text_emotions() -> Dict[str, Any]:
        """Return default text emotions"""
        return {
            'dominant_emotion': 'neutral',
            'dominant_emotion_score': 0.5,
            'emotion_distribution': {'neutral': 1.0},
            'analyzed_sentences': 0,
        }
    
    @staticmethod
    def _get_default_combined_emotions() -> Dict[str, Any]:
        """Return default combined emotions"""
        return {
            'audio_emotions': EmotionAnalyzer._get_default_audio_emotions(),
            'text_emotions': EmotionAnalyzer._get_default_text_emotions(),
            'overall_emotional_state': {
                'emotional_intensity': 5.0,
                'emotional_confidence': 5.0,
                'emotional_alignment': 'unknown',
            },
        }
