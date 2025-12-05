# Shark Tank Pitch Analyzer - Quick Start Guide 🦈

## 60-Second Setup

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows: use this
# source venv/bin/activate  # macOS/Linux: use this

# 2. Install packages
pip install -r requirements.txt

# 3. Download spaCy model
python -m spacy download en_core_web_sm

# 4. Run!
streamlit run app.py
```

**That's it!** The app opens at `http://localhost:8501`

---

## What You Get

### 🎯 Instant Analysis
Upload a 30-second to 10-minute pitch and get:

1. **Vocal Delivery Score (0-10)**
   - Clarity: How articulate is your speech?
   - Energy: How enthusiastic are you?
   - Confidence: How steady is your delivery?

2. **Business Content Score (0-10)**
   - Problem: Is the problem clear?
   - Solution: Is the solution viable?
   - Market: Market opportunity understood?
   - Revenue Model: Business model explained?
   - Competition: Competitive advantage?

3. **Shark Feedback** from 5 personas:
   - Mark (Strategic Investor) 📈
   - Barbara (Finance Expert) 💰
   - Robert (Product Visionary) 🎨
   - Lori (Domain Expert) 🏆
   - Daymond (Aggressive Dealer) 🚀

4. **Consensus Verdict**
   - "Invest" - Strong potential (≥7.0 score)
   - "Need More Info" - Promising (≥5.0 score)
   - "Not Invest" - Needs work (<5.0 score)

---

## Key Features

✅ **Audio Analysis**
- Pitch, pace, volume, pauses extracted from your speech
- Emotion detection from voice and text
- Speech clarity and energy metrics

✅ **Smart Transcription**
- Auto speech-to-text using Whisper
- Word-level timestamps
- Confidence scores

✅ **Business Intelligence**
- Analyzes business logic in your pitch
- Scores problem, solution, market, revenue, competition
- Extracts key claims and business entities

✅ **AI Feedback Panel**
- 5 different investor personas
- Each provides personalized feedback
- Consensus recommendation

✅ **Export Results**
- Download detailed JSON analysis
- Archive for improvement tracking

---

## Example Workflow

```
1. Record or upload pitch (audio_pitch.wav)
   ↓
2. Click "Analyze Pitch" button
   ↓
3. Processing (~2-5 minutes on CPU, ~30 seconds on GPU)
   ├─ Extracts vocal features
   ├─ Transcribes speech
   ├─ Analyzes emotions
   ├─ Scores business content
   ├─ Gets shark feedback
   └─ Generates consensus
   ↓
4. View comprehensive results dashboard
   ├─ Overall score & verdict
   ├─ Detailed metric breakdowns
   ├─ Full transcription
   ├─ Shark-by-shark feedback
   ├─ Audio characteristics
   └─ Emotional analysis
   ↓
5. Download JSON for records
```

---

## Tips for Best Results

### 📱 Audio Recording
- **Quality:** Use a good microphone (phone/computer mic is fine)
- **Silence:** Record in quiet environment
- **Format:** WAV, MP3, M4A, FLAC, or OGG
- **Duration:** 30 seconds to 10 minutes

### 🗣️ Pitch Content
- **Problem:** Start with clear problem statement (why it matters)
- **Solution:** Explain your solution (how you solve it)
- **Market:** Show market opportunity (size, growth potential)
- **Revenue:** Describe revenue model (how you make money)
- **Competition:** Address competitors (your differentiation)

### 🎤 Delivery Tips
- **Clarity:** Speak clearly and articulate
- **Energy:** Show enthusiasm for your idea
- **Confidence:** Project confidence in your business
- **Pace:** Don't rush or speak too slowly
- **Pauses:** Use natural pauses, avoid "ums" and "ahs"

---

## Understanding Your Scores

### Vocal Delivery (50% of final score)

**Clarity (0-10)**
- 8+: Very clear, excellent articulation
- 5-7: Clear enough, minor issues
- <5: Hard to understand, clarity issues

**Energy (0-10)**
- 8+: Highly energetic, great enthusiasm
- 5-7: Decent energy, could be better
- <5: Low energy, sounds uninterested

**Confidence (0-10)**
- 8+: Very confident, steady delivery
- 5-7: Mostly confident, some wavering
- <5: Nervous, lacks confidence

### Business Content (50% of final score)

**Problem/Solution/Market/Revenue/Competition (0-10 each)**
- 8+: Well explained, clear and compelling
- 5-7: Adequate explanation, room for improvement
- <5: Unclear, underdeveloped

---

## Shark Personas Explained

### Mark - Strategic Investor 📈
**Focus:** Market size, growth, scalability, execution
**Verdict:** Invests if market is huge and scalable

### Barbara - Finance Expert 💰
**Focus:** Unit economics, profitability, cash flow, burn rate
**Verdict:** Invests if numbers make sense

### Robert - Product Visionary 🎨
**Focus:** Product quality, user experience, differentiation
**Verdict:** Invests if product is innovative and well-designed

### Lori - Domain Expert 🏆
**Focus:** Industry knowledge, partnerships, execution capability
**Verdict:** Invests if team understands their space

### Daymond - Aggressive Dealer 🚀
**Focus:** Brand potential, market timing, customer acquisition
**Verdict:** Invests if there's huge brand potential

---

## Troubleshooting

**Q: App won't start**
```bash
# Check Python is installed
python --version

# Check virtual environment is active
# You should see (venv) at the start of terminal line

# Reinstall packages
pip install -r requirements.txt --upgrade
```

**Q: Slow processing**
- Processing takes 2-5 minutes on CPU
- For faster results, use GPU (see SETUP.md)
- Or use smaller models (edit src/config.py)

**Q: Out of memory**
- Edit src/config.py and set WHISPER_MODEL = "tiny"
- Use smaller LLM model

**Q: spaCy model not found**
```bash
python -m spacy download en_core_web_sm
```

**Q: Error downloading models**
```bash
# Manually download
huggingface-cli download distilbert-base-uncased
```

---

## Performance Guide

### Laptop (8GB RAM, CPU)
- Avg time: 4-5 minutes
- Model size: "tiny" Whisper, smaller LLM
- Edit src/config.py:
  ```python
  WHISPER_MODEL = "tiny"
  LLM_MODEL = "distilgpt2"
  ```

### Desktop (16GB RAM, CPU)
- Avg time: 2-3 minutes
- Model size: "small" or "base" Whisper
- Default config is fine

### Workstation (16GB+ RAM, GPU)
- Avg time: 30-60 seconds
- Model size: "medium" or "large" Whisper
- Edit .env:
  ```env
  WHISPER_DEVICE=cuda
  ```

---

## File Structure

```
SharkTankPitchAnalyzer/
├── app.py                  ← Run this to start
├── requirements.txt        ← Install these packages
├── README.md              ← Full documentation
├── SETUP.md               ← Detailed setup guide
├── QUICK_START.md         ← This file
├── test_installation.py   ← Test your setup
│
├── src/                   ← Core modules
│   ├── config.py         ← Settings and constants
│   ├── utils.py          ← Helper functions
│   ├── audio_processor.py    ← Audio analysis
│   ├── transcription.py      ← Speech-to-text
│   ├── emotion_analyzer.py   ← Emotion detection
│   ├── transcript_analyzer.py ← Text analysis
│   ├── scorer.py            ← Scoring logic
│   └── feedback_engine.py    ← Shark feedback
│
├── data/                  ← Data files
│   ├── audio/            ← Uploaded audio files
│   └── results/          ← Analysis results (JSON)
│
└── models/               ← Model cache
```

---

## Next Steps

1. **Setup complete?**
   ```bash
   python test_installation.py
   ```

2. **Start the app:**
   ```bash
   streamlit run app.py
   ```

3. **Try your first pitch!**
   - Record or find a pitch audio
   - Upload to the app
   - Wait for analysis
   - Review results

4. **Improve and iterate:**
   - Read feedback from each shark
   - Identify weak areas (clarity, energy, business logic)
   - Re-record and analyze again
   - Track improvement over time

---

## Common Questions

**Q: Can I use video?**
A: Not yet, audio only. Video support coming soon!

**Q: Is my data private?**
A: Yes! Everything runs locally on your computer. No uploads to servers.

**Q: Can I customize the sharks?**
A: Yes! Edit src/config.py → SHARK_PERSONAS

**Q: How often should I analyze?**
A: Record multiple takes, analyze each one, pick the best!

**Q: Can I compare multiple pitches?**
A: Yes! Results are saved as JSON, download and compare.

---

## Need Help?

1. **Installation issues?** → See SETUP.md
2. **Feature questions?** → See README.md
3. **Error messages?** → Check test_installation.py
4. **Code help?** → Check comments in src/ files

---

## Remember

✨ **This tool is your practice partner, not your judge.**

Use it to:
- Identify delivery weaknesses
- Strengthen business pitch
- Get objective feedback
- Build confidence
- Iterate and improve

Success depends on YOU taking action on the feedback! 🚀

---

**Ready? Let's analyze some pitches! 🦈**

```bash
streamlit run app.py
```
