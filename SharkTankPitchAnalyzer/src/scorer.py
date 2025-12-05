"""Scoring Module - Vocal Delivery and Business Content Scoring"""

import logging
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from config import VOCAL_DELIVERY_WEIGHTS, BUSINESS_CONTENT_WEIGHTS, VERDICT_THRESHOLDS
from utils import normalize_score, calculate_weighted_average

logger = logging.getLogger(__name__)


class VocalDeliveryScorer:
    """
    Scores vocal delivery based on acoustic features.
    Evaluates clarity, energy, and confidence from audio analysis.
    """
    
    def __init__(self):
        """Initialize vocal delivery scorer"""
        self.scaler = MinMaxScaler(feature_range=(0, 10))
        logger.info("VocalDeliveryScorer initialized")
    
    def score_clarity(self, vocal_features: Dict[str, Any]) -> float:
        """
        Score vocal clarity based on acoustic features
        
        Clarity is measured by:
        - Low pause frequency (fewer interruptions)
        - Pitch consistency (less variation)
        - Good spectral centroid (clear articulation)
        
        Args:
            vocal_features: Dictionary from audio processor
        
        Returns:
            Clarity score (0-10)
        """
        try:
            logger.info("Scoring clarity...")
            
            pause_features = vocal_features.get('pauses', {})
            pace_features = vocal_features.get('pace', {})
            volume_features = vocal_features.get('volume', {})
            
            # Pause frequency should be low (good clarity = few pauses)
            pause_freq = pause_features.get('pause_frequency', 0)
            pause_score = max(0, 10 - pause_freq * 5)  # Fewer pauses = higher score
            
            # Pitch variation should be moderate (not too much variation)
            pitch_features = vocal_features.get('pitch', {})
            pitch_variety = pitch_features.get('pitch_variety', 0)
            pitch_score = 10 - min(10, pitch_variety * 2)  # Some variety is good, but not too much
            
            # Spectral centroid indicates articulation clarity
            spectral_std = pace_features.get('spectral_centroid_std', 0)
            spectral_score = 10 - min(10, spectral_std / 2000 * 10)  # Lower std = clearer
            
            # ZCR (voice quality)
            zcr = pace_features.get('zero_crossing_rate', 0)
            zcr_score = min(10, zcr * 100)  # Higher ZCR = more fricatives = clearer
            
            # Combine scores
            clarity_score = (pause_score * 0.3 + pitch_score * 0.3 + spectral_score * 0.2 + zcr_score * 0.2)
            
            logger.info(f"Clarity score: {clarity_score:.2f}/10")
            return float(max(0, min(10, clarity_score)))
        
        except Exception as e:
            logger.error(f"Error scoring clarity: {e}")
            return 5.0
    
    def score_energy(self, vocal_features: Dict[str, Any]) -> float:
        """
        Score vocal energy and enthusiasm
        
        Energy is measured by:
        - RMS energy level (volume)
        - Dynamic range (variation in volume)
        - Tempo and onset frequency
        
        Args:
            vocal_features: Dictionary from audio processor
        
        Returns:
            Energy score (0-10)
        """
        try:
            logger.info("Scoring energy...")
            
            volume_features = vocal_features.get('volume', {})
            pace_features = vocal_features.get('pace', {})
            
            # RMS energy should be moderate to high
            rms_mean = volume_features.get('rms_energy_mean', 0)
            rms_score = min(10, rms_mean * 50)  # Normalize to 0-10
            
            # Dynamic range indicates energy variation
            dynamic_range = volume_features.get('dynamic_range', 0)
            range_score = min(10, dynamic_range * 30)  # Good energy has variation
            
            # Tempo indicates pace/energy
            tempo = pace_features.get('tempo_bpm', 0)
            # Normal speech ~140-180 BPM, excited speech higher
            tempo_score = min(10, (tempo / 200) * 10)
            
            # Onset count indicates dynamic changes
            onset_count = pace_features.get('onset_count', 0)
            duration = vocal_features.get('duration_seconds', 1)
            onset_freq = onset_count / max(1, duration)
            onset_score = min(10, onset_freq / 5 * 10)  # More onsets = more energy
            
            # Combine scores
            energy_score = (rms_score * 0.4 + range_score * 0.3 + tempo_score * 0.15 + onset_score * 0.15)
            
            logger.info(f"Energy score: {energy_score:.2f}/10")
            return float(max(0, min(10, energy_score)))
        
        except Exception as e:
            logger.error(f"Error scoring energy: {e}")
            return 5.0
    
    def score_confidence(self, vocal_features: Dict[str, Any], emotion_analysis: Dict[str, Any]) -> float:
        """
        Score vocal confidence based on acoustic features and emotional state
        
        Confidence is measured by:
        - Pitch stability (not too variable)
        - Lower jitter/shimmer (steady voice)
        - Emotional intensity
        
        Args:
            vocal_features: Dictionary from audio processor
            emotion_analysis: Dictionary from emotion analyzer
        
        Returns:
            Confidence score (0-10)
        """
        try:
            logger.info("Scoring confidence...")
            
            pitch_features = vocal_features.get('pitch', {})
            volume_features = vocal_features.get('volume', {})
            
            # Pitch stability - lower std = more confident
            pitch_std = pitch_features.get('std_pitch_hz', 0)
            pitch_mean = pitch_features.get('mean_pitch_hz', 1)
            pitch_cv = (pitch_std / max(1, pitch_mean))  # Coefficient of variation
            pitch_confidence = 10 - min(10, pitch_cv * 3)
            
            # Spectral stability - lower std = steadier voice
            spectral_std = volume_features.get('spectral_energy_std', 0)
            spectral_confidence = 10 - min(10, spectral_std / 10)
            
            # MFCC stability indicates consistent vocal quality
            mfcc_std = volume_features.get('mfcc_std', 0)
            mfcc_confidence = 10 - min(10, mfcc_std / 2)
            
            # Emotional intensity as confidence indicator
            emotional_intensity = emotion_analysis.get('overall_emotional_state', {}).get('emotional_intensity', 5)
            emotion_confidence = min(10, emotional_intensity)
            
            # Voiced percentage (more voiced = more confident speaking)
            voiced_pct = pitch_features.get('voiced_percentage', 0)
            voiced_confidence = min(10, voiced_pct / 10)
            
            # Combine scores
            confidence_score = (
                pitch_confidence * 0.25 +
                spectral_confidence * 0.25 +
                mfcc_confidence * 0.15 +
                emotion_confidence * 0.2 +
                voiced_confidence * 0.15
            )
            
            logger.info(f"Confidence score: {confidence_score:.2f}/10")
            return float(max(0, min(10, confidence_score)))
        
        except Exception as e:
            logger.error(f"Error scoring confidence: {e}")
            return 5.0
    
    def score_vocal_delivery(
        self,
        vocal_features: Dict[str, Any],
        emotion_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive vocal delivery score
        
        Args:
            vocal_features: Dictionary from audio processor
            emotion_analysis: Dictionary from emotion analyzer
        
        Returns:
            Dictionary with individual and weighted scores
        """
        try:
            logger.info("Calculating vocal delivery score...")
            
            clarity = self.score_clarity(vocal_features)
            energy = self.score_energy(vocal_features)
            confidence = self.score_confidence(vocal_features, emotion_analysis)
            
            # Calculate weighted average
            delivery_scores = {
                'clarity': clarity,
                'energy': energy,
                'confidence': confidence,
            }
            
            weighted_score = calculate_weighted_average(delivery_scores, VOCAL_DELIVERY_WEIGHTS)
            
            result = {
                'clarity': clarity,
                'energy': energy,
                'confidence': confidence,
                'overall_score': weighted_score,
                'weights': VOCAL_DELIVERY_WEIGHTS,
            }
            
            logger.info(f"Vocal delivery score: {weighted_score:.2f}/10")
            return result
        
        except Exception as e:
            logger.error(f"Error calculating vocal delivery score: {e}")
            return {
                'clarity': 0,
                'energy': 0,
                'confidence': 0,
                'overall_score': 0,
                'weights': VOCAL_DELIVERY_WEIGHTS,
            }


class BusinessContentScorer:
    """
    Scores business content based on transcript analysis.
    Evaluates problem clarity, market understanding, revenue model, etc.
    """
    
    def __init__(self):
        """Initialize business content scorer"""
        logger.info("BusinessContentScorer initialized")
    
    def score_business_content(self, transcript_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate business content score from transcript analysis
        
        Args:
            transcript_analysis: Dictionary from transcript analyzer
        
        Returns:
            Dictionary with business content scores
        """
        try:
            logger.info("Calculating business content score...")
            
            business_content = transcript_analysis.get('business_content', {})
            
            # Extract specific metrics
            problem_clarity = business_content.get('problem_clarity', 0) * 10  # Convert to 0-10 scale
            solution_quality = business_content.get('solution_quality', 0) * 10
            market_understanding = business_content.get('market_understanding', 0) * 10
            revenue_model = business_content.get('revenue_model', 0) * 10
            competitive_position = business_content.get('competitive_position', 0) * 10
            
            # Get preprocessing info for additional context
            preprocessing = transcript_analysis.get('preprocessing', {})
            team_mentions = len([e for e in preprocessing.get('entities', []) if e[1] == 'PERSON'])
            team_credibility = min(10, team_mentions * 2)  # More people mentioned = more credible
            
            # Language complexity affects clarity
            language_metrics = transcript_analysis.get('language_metrics', {})
            reading_ease = language_metrics.get('reading_ease', 50) / 10  # Convert to 0-10
            
            # Sentiment indicates positive tone
            sentiment = transcript_analysis.get('sentiment', {})
            sentiment_score = sentiment.get('overall_sentiment', 0.5) * 10
            
            content_scores = {
                'problem': min(10, problem_clarity),
                'solution': min(10, solution_quality),
                'market': min(10, market_understanding),
                'revenue_model': min(10, revenue_model),
                'competition': min(10, competitive_position),
                'clarity': min(10, reading_ease),
                'sentiment': sentiment_score,
                'team': team_credibility,
            }
            
            # Calculate weighted average using business content weights
            weights = BUSINESS_CONTENT_WEIGHTS.copy()
            # Add clarity as part of overall content score
            weighted_score = calculate_weighted_average(
                {k: v for k, v in content_scores.items() if k in weights},
                weights
            )
            
            result = {
                'problem': content_scores['problem'],
                'solution': content_scores['solution'],
                'market': content_scores['market'],
                'revenue_model': content_scores['revenue_model'],
                'competition': content_scores['competition'],
                'team_credibility': team_credibility,
                'clarity': content_scores['clarity'],
                'sentiment': sentiment_score,
                'overall_score': weighted_score,
                'weights': BUSINESS_CONTENT_WEIGHTS,
            }
            
            logger.info(f"Business content score: {weighted_score:.2f}/10")
            return result
        
        except Exception as e:
            logger.error(f"Error calculating business content score: {e}")
            return {
                'problem': 0,
                'solution': 0,
                'market': 0,
                'revenue_model': 0,
                'competition': 0,
                'team_credibility': 0,
                'clarity': 0,
                'sentiment': 5,
                'overall_score': 0,
                'weights': BUSINESS_CONTENT_WEIGHTS,
            }


class PitchScorer:
    """
    Comprehensive pitch scoring combining vocal delivery and business content.
    Produces final investment verdicts.
    """
    
    def __init__(self):
        """Initialize pitch scorer"""
        self.vocal_scorer = VocalDeliveryScorer()
        self.content_scorer = BusinessContentScorer()
        logger.info("PitchScorer initialized")
    
    def score_pitch(
        self,
        vocal_features: Dict[str, Any],
        emotion_analysis: Dict[str, Any],
        transcript_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive pitch score
        
        Args:
            vocal_features: From audio processor
            emotion_analysis: From emotion analyzer
            transcript_analysis: From transcript analyzer
        
        Returns:
            Dictionary with all scores and verdict
        """
        try:
            logger.info("Calculating comprehensive pitch score...")
            
            # Score vocal delivery
            vocal_score = self.vocal_scorer.score_vocal_delivery(vocal_features, emotion_analysis)
            
            # Score business content
            content_score = self.content_scorer.score_business_content(transcript_analysis)
            
            # Calculate overall score (50/50 split between delivery and content)
            overall_score = (vocal_score['overall_score'] * 0.5 + content_score['overall_score'] * 0.5)
            
            # Determine verdict
            verdict = self._determine_verdict(overall_score)
            
            comprehensive_score = {
                'vocal_delivery': vocal_score,
                'business_content': content_score,
                'overall_score': float(overall_score),
                'verdict': verdict,
                'pitch_summary': self._generate_pitch_summary(vocal_score, content_score, overall_score),
            }
            
            logger.info(f"Pitch scoring complete. Verdict: {verdict}")
            return comprehensive_score
        
        except Exception as e:
            logger.error(f"Error scoring pitch: {e}")
            raise
    
    def _determine_verdict(self, score: float) -> str:
        """
        Determine investment verdict based on score
        
        Args:
            score: Overall pitch score (0-10)
        
        Returns:
            Verdict string
        """
        if score >= VERDICT_THRESHOLDS['invest_min']:
            return "Invest"
        elif score >= VERDICT_THRESHOLDS['maybe_min']:
            return "Need More Info"
        else:
            return "Not Invest"
    
    def _generate_pitch_summary(
        self,
        vocal_score: Dict[str, float],
        content_score: Dict[str, float],
        overall_score: float
    ) -> str:
        """Generate brief summary of pitch performance"""
        summary_parts = []
        
        # Vocal delivery insights
        if vocal_score['clarity'] > 7:
            summary_parts.append("Clear and articulate delivery")
        elif vocal_score['clarity'] < 5:
            summary_parts.append("Clarity could be improved")
        
        if vocal_score['energy'] > 7:
            summary_parts.append("High energy and enthusiasm")
        elif vocal_score['energy'] < 5:
            summary_parts.append("More energy and enthusiasm needed")
        
        if vocal_score['confidence'] > 7:
            summary_parts.append("Confident presentation")
        elif vocal_score['confidence'] < 5:
            summary_parts.append("Could project more confidence")
        
        # Business content insights
        if content_score['problem'] > 7:
            summary_parts.append("Problem well articulated")
        
        if content_score['market'] > 7:
            summary_parts.append("Strong market understanding")
        elif content_score['market'] < 5:
            summary_parts.append("Market opportunity needs clarification")
        
        if content_score['revenue_model'] < 5:
            summary_parts.append("Revenue model needs development")
        
        if overall_score > 7:
            summary_parts.append("Strong investment potential")
        elif overall_score < 5:
            summary_parts.append("Significant improvements needed")
        
        return ". ".join(summary_parts) if summary_parts else "Mixed performance across metrics."
