# Shark Tank Pitch Analyzer - Setup Guide

## Quick Start (5 minutes)

### 1. Install Python
Ensure Python 3.8+ is installed:
```bash
python --version
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

### 4. Download NLP Models
```bash
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt stopwords averaged_perceptron_tagger
```

### 5. Run Application
```bash
streamlit run app.py
```

Access at: `http://localhost:8501`

---

## Detailed Installation

### System Requirements

**Minimum:**
- Python 3.8+
- 8GB RAM
- 5GB disk space (for models)
- CPU-based processing

**Recommended:**
- Python 3.10+
- 16GB RAM
- GPU (NVIDIA CUDA 11.8+) for faster processing
- SSD with 10GB+ free space

### Step-by-Step Installation

#### A. Windows

```bash
# 1. Clone/Download project
cd SharkTankPitchAnalyzer

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Upgrade pip
python -m pip install --upgrade pip

# 4. Install dependencies
pip install -r requirements.txt

# 5. Download models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"

# 6. Run app
streamlit run app.py
```

#### B. macOS

```bash
# 1. Clone/Download project
cd SharkTankPitchAnalyzer

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Upgrade pip
python -m pip install --upgrade pip

# 4. Install dependencies
pip install -r requirements.txt

# 5. Download models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"

# 6. Run app
streamlit run app.py
```

#### C. Linux (Ubuntu/Debian)

```bash
# 1. Install system dependencies
sudo apt-get update
sudo apt-get install python3-dev python3-pip python3-venv

# 2. Clone/Download project
cd SharkTankPitchAnalyzer

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Upgrade pip
python -m pip install --upgrade pip

# 5. Install dependencies
pip install -r requirements.txt

# 6. Download models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger')"

# 7. Run app
streamlit run app.py
```

### GPU Support (Optional)

For faster processing with NVIDIA GPU:

```bash
# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify GPU availability
python -c "import torch; print(torch.cuda.is_available())"
```

Then update `.env`:
```
WHISPER_DEVICE=cuda
```

### Troubleshooting Installation

#### Issue: ModuleNotFoundError

**Solution:** Ensure virtual environment is activated and all packages installed:
```bash
pip install -r requirements.txt --upgrade
```

#### Issue: spaCy model not found

**Solution:** Download manually:
```bash
python -m spacy download en_core_web_sm
```

#### Issue: Out of memory errors

**Solution:** Use smaller models. Edit `src/config.py`:
```python
WHISPER_MODEL = "tiny"  # instead of "base"
```

#### Issue: Slow performance on CPU

**Solution:** 
1. Install GPU support (see GPU Support section above)
2. Use smaller models (tiny/small)
3. Reduce LLM model size

---

## Configuration

### Basic Configuration (src/config.py)

```python
# Audio Settings
SAMPLE_RATE = 16000  # Hz
AUDIO_DURATION_MIN = 30  # seconds
AUDIO_DURATION_MAX = 600  # 10 minutes

# Model Selection
WHISPER_MODEL = "base"  # Options: tiny, base, small, medium, large
LLM_MODEL = "mistralai/Mistral-7B-Instruct-v0.1"

# Scoring Thresholds
VERDICT_THRESHOLDS = {
    "invest_min": 7.0,      # >= 7.0 = Invest
    "maybe_min": 5.0,       # >= 5.0 = Need More Info
}
```

### Environment Variables (.env)

```env
# GPU/Device
WHISPER_DEVICE=cpu  # or "cuda"

# API Keys (Optional)
OPENAI_API_KEY=your_key
HUGGINGFACE_API_KEY=your_key

# Model Configuration
LLM_TEMPERATURE=0.7  # 0.0-1.0
LLM_MAX_TOKENS=500
```

---

## First Run Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip list` should show all packages)
- [ ] spaCy model downloaded (`python -m spacy download en_core_web_sm`)
- [ ] NLTK data downloaded
- [ ] App starts without errors (`streamlit run app.py`)
- [ ] Streamlit opens in browser at `http://localhost:8501`

---

## Testing Installation

### Quick Test

```python
# test_installation.py
import librosa
import whisper
import spacy
import nltk
from transformers import pipeline
import streamlit

print("✓ All imports successful!")
print(f"spaCy models: {spacy.cli.models()}")
print("Ready to run Shark Tank Pitch Analyzer!")
```

Run:
```bash
python test_installation.py
```

---

## Performance Optimization

### For Laptops (Limited Resources)

```python
# Edit src/config.py
WHISPER_MODEL = "tiny"
LLM_MODEL = "distilgpt2"
SAMPLE_RATE = 16000
```

### For Workstations (Optimal Performance)

```python
# Edit src/config.py
WHISPER_MODEL = "medium"
LLM_MODEL = "meta-llama/Llama-2-13b-hf"
SAMPLE_RATE = 22050
```

---

## Uninstallation

To completely remove the installation:

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
# Windows:
rmdir /s venv
# macOS/Linux:
rm -rf venv

# Optional: Clear cache directories
rm -rf ~/.cache/huggingface
rm -rf ~/.cache/torch
```

---

## Getting Help

If you encounter issues:

1. **Check logs:**
   - Streamlit logs appear in the terminal
   - Check console for error messages

2. **Common issues:**
   - See README.md Troubleshooting section
   - Check model downloads are complete

3. **Manual model download:**
   ```bash
   huggingface-cli login  # If needed
   huggingface-cli download distilbert-base-uncased
   ```

---

## Next Steps

After installation:
1. Read `README.md` for feature overview
2. Prepare a sample pitch audio (WAV, MP3, etc.)
3. Upload and analyze!
4. Check `data/results/` for saved analyses

---

**Happy Analyzing! 🦈**
