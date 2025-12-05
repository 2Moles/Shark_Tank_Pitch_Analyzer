"""Transcript Analysis Module - Text Processing and Business Logic Scoring"""

import logging
from typing import Dict, List, Any, Tuple
import re
from collections import Counter
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
import spacy
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger', quiet=True)


class TranscriptAnalyzer:
    """
    Analyzes pitch transcripts for business content and messaging clarity.
    Uses spaCy for NLP and Hugging Face transformers for business logic scoring.
    """
    
    def __init__(self):
        """Initialize transcript analyzer with NLP models"""
        self.nlp = None
        self.zero_shot_classifier = None
        self.sentiment_pipeline = None
        self._initialize_models()
    
    def _initialize_models(self) -> None:
        """Initialize NLP models"""
        try:
            logger.info("Initializing NLP models...")
            
            # Load spaCy model
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("Downloading spaCy model...")
                import subprocess
                subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
                self.nlp = spacy.load("en_core_web_sm")
            
            # Zero-shot classifier for business aspects
            self.zero_shot_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if self._has_cuda() else -1
            )
            
            # Sentiment analysis
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=0 if self._has_cuda() else -1
            )
            
            logger.info("NLP models initialized successfully")
        
        except Exception as e:
            logger.error(f"Error initializing NLP models: {e}")
            self.nlp = None
            self.zero_shot_classifier = None
            self.sentiment_pipeline = None
    
    @staticmethod
    def _has_cuda() -> bool:
        """Check if CUDA is available"""
        try:
            return torch.cuda.is_available()
        except:
            return False
    
    def preprocess_transcript(self, text: str) -> Dict[str, Any]:
        """
        Preprocess transcript text
        
        Args:
            text: Raw transcript
        
        Returns:
            Dictionary with preprocessed text and linguistic features
        """
        try:
            logger.info("Preprocessing transcript...")
            
            # Basic cleaning
            cleaned_text = re.sub(r'\s+', ' ', text).strip()
            
            # Tokenize
            sentences = sent_tokenize(cleaned_text)
            words = word_tokenize(cleaned_text.lower())
            
            # Remove stopwords
            stop_words = set(stopwords.words('english'))
            filtered_words = [w for w in words if w.isalnum() and w not in stop_words]
            
            # POS tagging
            pos_tags = pos_tag(word_tokenize(cleaned_text))
            
            # spaCy processing
            doc = self.nlp(cleaned_text) if self.nlp else None
            
            entities = []
            noun_phrases = []
            
            if doc:
                entities = [(ent.text, ent.label_) for ent in doc.ents]
                noun_phrases = [chunk.text for chunk in doc.noun_chunks]
            
            preprocessing_result = {
                'cleaned_text': cleaned_text,
                'sentences': sentences,
                'sentence_count': len(sentences),
                'words': filtered_words,
                'word_count': len(filtered_words),
                'vocabulary_diversity': len(set(filtered_words)) / len(filtered_words) if filtered_words else 0,
                'pos_tags': pos_tags,
                'entities': entities,
                'noun_phrases': noun_phrases,
            }
            
            logger.info(f"Preprocessing complete: {len(sentences)} sentences, {len(filtered_words)} words")
            return preprocessing_result
        
        except Exception as e:
            logger.error(f"Error preprocessing transcript: {e}")
            return self._get_default_preprocessing()
    
    def analyze_business_content(self, text: str) -> Dict[str, Any]:
        """
        Analyze business aspects of the pitch (problem, solution, market, revenue model, competition)
        
        Args:
            text: Pitch transcript
        
        Returns:
            Dictionary with business content scores
        """
        try:
            logger.info("Analyzing business content...")
            
            if not self.zero_shot_classifier:
                return self._get_default_business_analysis()
            
            # Define candidate labels for business aspects
            candidate_labels = [
                "problem statement",
                "solution description",
                "market opportunity",
                "revenue model",
                "competitive advantage",
                "team credentials",
                "funding ask",
                "use of funds",
            ]
            
            # Split text into sentences for analysis
            sentences = sent_tokenize(text)
            limited_sentences = sentences[:30]  # Limit to first 30 sentences to avoid token overflow
            
            business_scores = {aspect: [] for aspect in candidate_labels}
            
            # Analyze each sentence
            for sentence in limited_sentences:
                if len(sentence.split()) > 5:  # Only analyze substantial sentences
                    try:
                        result = self.zero_shot_classifier(
                            sentence,
                            candidate_labels,
                            multi_class=True,
                            hypothesis_template="This text discusses {}.",
                        )
                        
                        # Store scores for each aspect
                        for label, score in zip(result['labels'], result['scores']):
                            business_scores[label].append(score)
                    except Exception as e:
                        logger.debug(f"Error analyzing sentence: {e}")
                        continue
            
            # Calculate average scores for each aspect
            business_content = {}
            for aspect, scores in business_scores.items():
                if scores:
                    business_content[aspect] = float(sum(scores) / len(scores))
                else:
                    business_content[aspect] = 0.0
            
            # Map to required categories
            analysis_result = {
                'problem_clarity': business_content.get('problem statement', 0),
                'solution_quality': business_content.get('solution description', 0),
                'market_understanding': business_content.get('market opportunity', 0),
                'revenue_model': business_content.get('revenue model', 0),
                'competitive_position': business_content.get('competitive advantage', 0),
                'team_credibility': business_content.get('team credentials', 0),
                'ask_clarity': business_content.get('funding ask', 0),
                'all_aspects': business_content,
            }
            
            logger.info("Business content analysis complete")
            return analysis_result
        
        except Exception as e:
            logger.error(f"Error analyzing business content: {e}")
            return self._get_default_business_analysis()
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze overall sentiment and positivity of the pitch
        
        Args:
            text: Pitch transcript
        
        Returns:
            Dictionary with sentiment analysis
        """
        try:
            if not self.sentiment_pipeline:
                return self._get_default_sentiment()
            
            logger.info("Analyzing sentiment...")
            
            # Split into sentences for granular analysis
            sentences = sent_tokenize(text)
            limited_sentences = sentences[:20]  # Limit to avoid token overflow
            
            sentiment_results = []
            
            for sentence in limited_sentences:
                if len(sentence.split()) > 3:
                    try:
                        result = self.sentiment_pipeline(sentence[:512])[0]  # Limit to 512 chars
                        sentiment_results.append({
                            'sentence': sentence[:100],
                            'label': result['label'],
                            'score': result['score'],
                        })
                    except Exception as e:
                        logger.debug(f"Error analyzing sentiment: {e}")
                        continue
            
            if not sentiment_results:
                return self._get_default_sentiment()
            
            # Calculate aggregate sentiment
            positive_score = sum(r['score'] for r in sentiment_results if r['label'] == 'POSITIVE')
            negative_score = sum(r['score'] for r in sentiment_results if r['label'] == 'NEGATIVE')
            
            total_score = positive_score + negative_score
            if total_score == 0:
                overall_sentiment = 0.5
            else:
                overall_sentiment = positive_score / total_score
            
            sentiment_analysis = {
                'overall_sentiment': float(overall_sentiment),
                'positive_sentences': len([r for r in sentiment_results if r['label'] == 'POSITIVE']),
                'negative_sentences': len([r for r in sentiment_results if r['label'] == 'NEGATIVE']),
                'sentiment_distribution': {
                    'positive': float(positive_score / total_score) if total_score > 0 else 0,
                    'negative': float(negative_score / total_score) if total_score > 0 else 0,
                },
            }
            
            logger.info(f"Sentiment analysis complete: {sentiment_analysis['overall_sentiment']:.2f}")
            return sentiment_analysis
        
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return self._get_default_sentiment()
    
    def extract_key_claims(self, text: str, n: int = 10) -> List[str]:
        """
        Extract key claims and statements from the pitch
        
        Args:
            text: Pitch transcript
            n: Number of key claims to extract
        
        Returns:
            List of key claims
        """
        try:
            logger.info(f"Extracting top {n} key claims...")
            
            sentences = sent_tokenize(text)
            
            if not self.nlp:
                # Fallback: return longest sentences
                return sorted(sentences, key=len, reverse=True)[:n]
            
            # Score sentences by importance (based on entities and noun phrases)
            scored_sentences = []
            
            for sentence in sentences:
                doc = self.nlp(sentence)
                
                # Count entities and complex noun phrases
                entity_count = len(doc.ents)
                noun_phrase_count = len(list(doc.noun_chunks))
                sentence_length = len(doc)
                
                score = entity_count * 2 + noun_phrase_count + sentence_length * 0.1
                scored_sentences.append((sentence, score))
            
            # Return top sentences by score
            key_claims = [sent for sent, score in sorted(scored_sentences, key=lambda x: x[1], reverse=True)[:n]]
            
            logger.info(f"Extracted {len(key_claims)} key claims")
            return key_claims
        
        except Exception as e:
            logger.error(f"Error extracting key claims: {e}")
            return []
    
    def analyze_language_complexity(self, text: str) -> Dict[str, Any]:
        """
        Analyze language complexity and clarity
        
        Args:
            text: Pitch transcript
        
        Returns:
            Dictionary with language metrics
        """
        try:
            logger.info("Analyzing language complexity...")
            
            # Calculate readability metrics
            sentences = sent_tokenize(text)
            words = word_tokenize(text)
            
            avg_sentence_length = len(words) / len(sentences) if sentences else 0
            avg_word_length = sum(len(w) for w in words) / len(words) if words else 0
            
            # Flesch Kincaid approximation
            syllable_count = sum(self._count_syllables(word) for word in words)
            flesch_kincaid = max(0, min(18, 0.39 * avg_sentence_length + 11.8 * (syllable_count / len(words)) - 15.59))
            
            # Vocabulary analysis
            unique_words = len(set(w.lower() for w in words if w.isalnum()))
            
            language_metrics = {
                'avg_sentence_length': float(avg_sentence_length),
                'avg_word_length': float(avg_word_length),
                'flesch_kincaid_grade': float(flesch_kincaid),
                'vocabulary_richness': float(unique_words / len(words)) if words else 0,
                'reading_ease': self._flesch_reading_ease(avg_sentence_length, syllable_count, len(words)),
            }
            
            logger.info("Language complexity analysis complete")
            return language_metrics
        
        except Exception as e:
            logger.error(f"Error analyzing language complexity: {e}")
            return self._get_default_language_metrics()
    
    @staticmethod
    def _count_syllables(word: str) -> int:
        """Estimate syllable count in a word"""
        word = word.lower()
        syllable_count = 0
        vowels = "aeiouy"
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent 'e'
        if word.endswith('e'):
            syllable_count -= 1
        
        # Ensure at least 1 syllable
        return max(1, syllable_count)
    
    @staticmethod
    def _flesch_reading_ease(sentence_length: float, syllable_count: int, word_count: int) -> float:
        """Calculate Flesch Reading Ease score"""
        if word_count == 0:
            return 50.0
        
        score = 206.835 - 1.015 * sentence_length - 84.6 * (syllable_count / word_count)
        return max(0, min(100, score))
    
    def analyze_transcript(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive transcript analysis
        
        Args:
            text: Pitch transcript
        
        Returns:
            Complete analysis dictionary
        """
        try:
            logger.info("Starting comprehensive transcript analysis...")
            
            preprocessing = self.preprocess_transcript(text)
            business_analysis = self.analyze_business_content(text)
            sentiment = self.analyze_sentiment(text)
            key_claims = self.extract_key_claims(text)
            language_metrics = self.analyze_language_complexity(text)
            
            comprehensive_analysis = {
                'preprocessing': preprocessing,
                'business_content': business_analysis,
                'sentiment': sentiment,
                'key_claims': key_claims[:5],  # Top 5 claims
                'language_metrics': language_metrics,
            }
            
            logger.info("Comprehensive transcript analysis complete")
            return comprehensive_analysis
        
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            raise
    
    @staticmethod
    def _get_default_preprocessing() -> Dict[str, Any]:
        """Return default preprocessing result"""
        return {
            'cleaned_text': '',
            'sentences': [],
            'sentence_count': 0,
            'words': [],
            'word_count': 0,
            'vocabulary_diversity': 0,
            'pos_tags': [],
            'entities': [],
            'noun_phrases': [],
        }
    
    @staticmethod
    def _get_default_business_analysis() -> Dict[str, Any]:
        """Return default business analysis"""
        return {
            'problem_clarity': 0,
            'solution_quality': 0,
            'market_understanding': 0,
            'revenue_model': 0,
            'competitive_position': 0,
            'team_credibility': 0,
            'ask_clarity': 0,
            'all_aspects': {},
        }
    
    @staticmethod
    def _get_default_sentiment() -> Dict[str, Any]:
        """Return default sentiment analysis"""
        return {
            'overall_sentiment': 0.5,
            'positive_sentences': 0,
            'negative_sentences': 0,
            'sentiment_distribution': {'positive': 0.5, 'negative': 0.5},
        }
    
    @staticmethod
    def _get_default_language_metrics() -> Dict[str, Any]:
        """Return default language metrics"""
        return {
            'avg_sentence_length': 0,
            'avg_word_length': 0,
            'flesch_kincaid_grade': 0,
            'vocabulary_richness': 0,
            'reading_ease': 50,
        }
