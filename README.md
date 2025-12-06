<img width="1111" height="628" alt="image" src="https://github.com/user-attachments/assets/9ffcf48a-5f3b-4d71-beb1-f73184b642ac" />

# Shark Tank Pitch Analyzer 🦈

An AI-powered analysis tool for evaluating Shark Tank-style pitches using open-source technology. Get comprehensive feedback from multiple investor personas on your pitch's vocal delivery and business content.

## Features


### 🎤 Audio Analysis
- **Vocal Feature Extraction** (Librosa)
  - Pitch analysis (mean, variation, range)
  - Speech pace and tempo
  - Volume, energy, and dynamic range
  - Pause detection and frequency
  - Voice quality metrics

### 🗣️ Speech-to-Text
- **Transcription** (OpenAI Whisper)
  - Automatic speech recognition
  - Multi-language support
  - Confidence scores and timestamps
  - Segment-level analysis

### 💭 Emotion Detection
- **Audio Emotions** (openSMILE + Librosa)
  - Acoustic emotion indicators
  - Energy and intensity analysis
- **Text Emotions** (Hugging Face Transformers)
  - Sentiment analysis
  - Dominant emotion detection
  - Emotional tone classification

### 📝 Transcript Analysis
- **NLP Processing** (spaCy, NLTK)
  - Entity recognition
  - Noun phrase extraction
  - Language complexity metrics
  - Readability scores (Flesch-Kincaid)
- **Business Content Scoring** (Transformers)
  - Problem clarity
  - Solution quality
  - Market understanding
  - Revenue model explanation
  - Competitive positioning

### 🎯 Comprehensive Scoring
- **Vocal Delivery Score**
  - Clarity (articulation, pauses, pitch consistency)
  - Energy (volume, dynamic range, tempo)
  - Confidence (pitch stability, vocal steadiness)
- **Business Content Score**
  - Problem, Solution, Market, Revenue Model, Competition

### 🦈 Multi-Shark Feedback
- **5 Investor Personas** (powered by Hugging Face LLMs)
  1. **Strategic Investor** - Growth and scalability focused
  2. **Finance Expert** - Numbers and profitability focused
  3. **Product Visionary** - Innovation and user experience focused
  4. **Domain Expert** - Industry knowledge and execution focused
  5. **Aggressive Dealer** - Brand and market timing focused
- **Consensus Verdict** - Panel-wide investment recommendation
- **Detailed Reasoning** - Persona-specific feedback and insights

### 📊 UI & Export
- **Streamlit Dashboard** with interactive visualizations
- **JSON Export** for detailed analysis archiving
- **Metric Dashboards** with scoring breakdowns

## Tech Stack

```
Audio & Speech:
- librosa (audio processing)
- soundfile (audio I/O)
- openai-whisper (speech recognition)

NLP & Text:
- spacy (information extraction)
- nltk (text processing)
- transformers (language models)
- huggingface_hub (model management)

Emotion & Analysis:
- opensmile (acoustic feature extraction)
- sentence-transformers (semantic analysis)
- scikit-learn (ML scoring)
- pandas (data processing)

LLM & Feedback:
- langchain (LLM orchestration)
- huggingface (open-source models)

UI:
- streamlit (web interface)
```

## Installation

### 1. Clone or Download

```bash
cd SharkTankPitchAnalyzer
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download Model Dependencies

Some models require additional downloads:

```bash
# spaCy model for English NLP
python -m spacy download en_core_web_sm

# NLTK data (if not auto-downloaded)
python -m nltk.downloader punkt stopwords averaged_perceptron_tagger
```

### 5. Setup Environment Variables (Optional)

Create a `.env` file in the project root:

```env
# Optional: Set GPU device
WHISPER_DEVICE=cuda  # or "cpu"

# Optional: API Keys for enhanced functionality
OPENAI_API_KEY=your_key_here
HUGGINGFACE_API_KEY=your_key_here
```

## Usage

### Running the Application

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Basic Workflow

1. **Upload Audio** - Upload a 30-second to 10-minute pitch recording
2. **Wait for Processing** - Audio analysis, transcription, and scoring (2-5 minutes)
3. **Review Results** - Scores, transcripts, audio metrics, and emotional analysis
4. **Read Feedback** - Multi-shark feedback panel and consensus verdict
5. **Export Results** - Download detailed JSON analysis

## Project Structure

```
SharkTankPitchAnalyzer/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── src/
│   ├── audio_processor.py         # Audio feature extraction (Librosa)
│   ├── transcription.py           # Speech-to-text (Whisper)
│   ├── emotion_analyzer.py        # Emotion detection (openSMILE + Transformers)
│   ├── transcript_analyzer.py     # Text analysis (spaCy, NLTK, Transformers)
│   ├── scorer.py                  # Vocal and business content scoring
│   ├── feedback_engine.py         # Multi-shark feedback (LangChain)
│   ├── config.py                  # Configuration and constants
│   └── utils.py                   # Utility functions
├── data/
│   ├── audio/                     # Uploaded audio files
│   └── results/                   # Analysis results
├── models/                        # Cached model files
└── tests/                         # Unit tests (optional)
```

## Configuration

Edit `src/config.py` to customize:

- Audio processing parameters (sample rate, FFT size, etc.)
- Model selections (Whisper size, LLM model, etc.)
- Scoring weights for vocal delivery and business content
- Shark persona definitions
- Verdict thresholds (invest/maybe/no)

### Key Configuration

```python
# config.py

# Audio Settings
SAMPLE_RATE = 16000  # Hz
AUDIO_DURATION_MIN = 30  # seconds
AUDIO_DURATION_MAX = 600  # 10 minutes

# Whisper Model
WHISPER_MODEL = "base"  # tiny, base, small, medium, large

# LLM Settings
LLM_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"
LLM_TEMPERATURE = 0.7

# Verdict Thresholds
VERDICT_THRESHOLDS = {
    "invest_min": 7.0,      # Score >= 7.0 -> Invest
    "maybe_min": 5.0,       # Score >= 5.0 -> Need More Info
}

# Scoring Weights (0-10 scale)
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
```

## Output Format

### Scores (0-10 scale)

**Vocal Delivery:**
- **Clarity**: Speech articulation, pause frequency, pitch consistency
- **Energy**: Volume level, dynamic range, speaking tempo
- **Confidence**: Vocal steadiness, pitch stability, emotional intensity

**Business Content:**
- **Problem**: Problem articulation and clarity
- **Solution**: Solution quality and feasibility
- **Market**: Market size and opportunity understanding
- **Revenue Model**: Business model clarity and viability
- **Competition**: Competitive positioning and differentiation

### Verdict

Three possible verdicts:
- **Invest** (score ≥ 7.0) - Strong investment potential
- **Need More Info** (score ≥ 5.0) - Promising but needs development
- **Not Invest** (score < 5.0) - Needs significant improvement

## Example Analysis Output

```json
{
  "overall_score": 7.2,
  "verdict": "Invest",
  "vocal_delivery": {
    "clarity": 7.5,
    "energy": 7.8,
    "confidence": 6.8,
    "overall_score": 7.4
  },
  "business_content": {
    "problem": 7.2,
    "solution": 7.0,
    "market": 6.8,
    "revenue_model": 7.5,
    "competition": 7.3,
    "overall_score": 7.1
  },
  "shark_feedback": [
    {
      "persona": "Mark (Strategic Investor)",
      "recommendation": "Strong Interest",
      "feedback": "Clear problem-solution fit with decent market sizing..."
    },
    // ... more shark feedback
  ],
  "consensus": {
    "overall_verdict": "Go For It!",
    "strong_interest_count": 4,
    "conditional_interest_count": 1,
    "not_interested_count": 0
  }
}
```

## Performance Tips

### For Faster Processing

1. **Use smaller Whisper model:**
   ```python
   WHISPER_MODEL = "tiny"  # or "small"
   ```

2. **Reduce LLM quality for speed:**
   ```python
   LLM_MODEL = "distilgpt2"  # Faster than larger models
   ```

3. **Use GPU if available:**
   ```env
   WHISPER_DEVICE=cuda
   ```

### For Better Accuracy

1. **Use larger Whisper model:**
   ```python
   WHISPER_MODEL = "medium"  # or "large"
   ```

2. **Use more advanced LLM:**
   ```python
   LLM_MODEL = "meta-llama/Llama-2-13b-hf"
   ```

## Troubleshooting

### Memory Issues

If you run out of memory:
```bash
# Use smaller model sizes
# Edit config.py and set:
WHISPER_MODEL = "tiny"
LLM_MODEL = "distilgpt2"
```

### GPU Not Detected

```bash
# Install GPU support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Model Download Errors

```bash
# Manually download models
huggingface-cli download distilbert-base-uncased
huggingface-cli download j-hartmann/emotion-english-distilroberta-base
```

## Future Enhancements

- [ ] Real-time audio processing and feedback
- [ ] Video analysis (body language, eye contact)
- [ ] Historical pitch comparison and improvement tracking
- [ ] Custom shark persona creation
- [ ] Integration with Zoom/Teams for live pitch analysis
- [ ] Multilingual pitch support
- [ ] A/B testing for pitch variations

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please feel free to submit pull requests or open issues.

## Support

For issues, questions, or suggestions:
1. Check the troubleshooting section
2. Review the code comments and docstrings
3. Open an issue on the project repository

## Disclaimer

This tool provides AI-generated analysis and should be used as one input among many. Always conduct your own due diligence and consult with qualified professionals before making investment decisions.

---

**Built with 🦈 **
