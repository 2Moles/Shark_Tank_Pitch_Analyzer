"""Configuration settings for Shark Tank Pitch Analyzer"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
AUDIO_DIR = DATA_DIR / "audio"
RESULTS_DIR = DATA_DIR / "results"

# Create directories if they don't exist
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Audio Processing Settings
SAMPLE_RATE = 16000  # Hz
AUDIO_DURATION_MIN = 30  # seconds
AUDIO_DURATION_MAX = 600  # seconds (10 minutes)
N_MELS = 128
N_FFT = 2048
HOP_LENGTH = 512

# Whisper Settings
WHISPER_MODEL = "base"  # base, small, medium, large
WHISPER_DEVICE = "cuda"  # or "cpu"

# Emotion Detection Settings
EMOTION_FEATURES = [
    "Loudness_sma3",
    "mfcc1-13",
    "spectralCentroid_sma3",
    "F0semitoneFrom27.5Hz_sma3nz",
]

# Transformer Models
BUSINESS_ANALYSIS_MODEL = "distilbert-base-uncased"
SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"

# Scoring Weights
VOCAL_DELIVERY_WEIGHTS = {
    "clarity": 0.35,
    "energy": 0.35,
    "confidence": 0.30,
}

BUSINESS_CONTENT_WEIGHTS = {
    "problem": 0.20,
    "solution": 0.20,
    "market": 0.20,
    "revenue_model": 0.20,
    "competition": 0.20,
}

# Shark Personas
SHARK_PERSONAS = {
    "strategic_investor": {
        "name": "Mark (Strategic Investor)",
        "archetype": "Tech-savvy, growth-focused, loves scalability",
        "focus_areas": ["market_size", "growth_potential", "scalability", "team"],
        "tone": "direct, analytical, no-nonsense",
    },
    "finance_expert": {
        "name": "Barbara (Finance Expert)",
        "archetype": "Numbers-driven, cash flow focused, practical",
        "focus_areas": ["revenue_model", "unit_economics", "profitability", "burn_rate"],
        "tone": "skeptical, detailed, data-focused",
    },
    "product_visionary": {
        "name": "Robert (Product Visionary)",
        "archetype": "Product-focused, innovation-driven, customer-centric",
        "focus_areas": ["product_quality", "user_experience", "differentiation", "problem_fit"],
        "tone": "thoughtful, critical, design-conscious",
    },
    "domain_expert": {
        "name": "Lori (Domain Expert)",
        "archetype": "Industry insider, knows the space deeply",
        "focus_areas": ["industry_knowledge", "competitive_position", "partnerships", "execution"],
        "tone": "experienced, specific, practical",
    },
    "aggressive_dealer": {
        "name": "Daymond (Aggressive Dealer)",
        "archetype": "Street-smart, brand-focused, hustler mentality",
        "focus_areas": ["brand_potential", "market_timing", "customer_acquisition", "hustle"],
        "tone": "energetic, street-smart, motivating",
    },
}

# LLM Settings
LLM_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"  # or "meta-llama/Llama-2-7b-hf"
LLM_MAX_TOKENS = 500
LLM_TEMPERATURE = 0.7

# Verdict Thresholds
VERDICT_THRESHOLDS = {
    "invest_min": 7.0,
    "maybe_min": 5.0,
    "not_invest_max": 5.0,
}

# API Keys (from environment variables)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
