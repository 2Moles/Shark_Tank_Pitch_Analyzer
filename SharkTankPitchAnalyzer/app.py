"""Shark Tank Pitch Analyzer - Streamlit Application"""

import streamlit as st
import logging
from pathlib import Path
import tempfile
import json
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import BASE_DIR, AUDIO_DIR, RESULTS_DIR
from audio_processor import AudioProcessor
from transcription import TranscriptionEngine
from emotion_analyzer import EmotionAnalyzer
from transcript_analyzer import TranscriptAnalyzer
from scorer import PitchScorer
from feedback_engine import SharkPersonaFeedbackEngine
from utils import save_results, format_timestamp, validate_audio_file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit page config
st.set_page_config(
    page_title="Shark Tank Pitch Analyzer",
    page_icon="🦈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
    .metric-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
    }
    .verdict-invest {
        background-color: #d4edda;
        color: #155724;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #28a745;
    }
    .verdict-maybe {
        background-color: #fff3cd;
        color: #856404;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
    }
    .verdict-no {
        background-color: #f8d7da;
        color: #721c24;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False


def display_header():
    """Display application header"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🦈 Shark Tank Pitch Analyzer")
        st.markdown("*AI-powered analysis of your pitch: Vocal delivery, business content, and investor feedback*")
    with col2:
        st.image("https://raw.githubusercontent.com/streamlit/streamlit/develop/docs/static/img/streamlit_icon.svg",
                 width=100)


def display_upload_section():
    """Display audio upload section"""
    st.header("📤 Upload Your Pitch")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload an audio file of your Shark Tank pitch",
            type=['wav', 'mp3', 'm4a', 'flac', 'ogg'],
            help="Audio should be 30 seconds to 10 minutes long"
        )
    
    with col2:
        st.markdown("### Supported Formats")
        st.markdown("- WAV\n- MP3\n- M4A\n- FLAC\n- OGG")
    
    return uploaded_file


def save_uploaded_file(uploaded_file) -> Path:
    """Save uploaded file temporarily"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            return Path(tmp_file.name)
    except Exception as e:
        logger.error(f"Error saving uploaded file: {e}")
        raise


def validate_and_process_audio(audio_path: Path) -> tuple:
    """Validate audio file and return result"""
    is_valid, message = validate_audio_file(audio_path)
    
    if not is_valid:
        return is_valid, message
    
    return True, message


def display_processing_status(status_container):
    """Display processing status updates"""
    with status_container:
        st.info("⏳ Processing your pitch... This may take a few minutes.")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        return progress_bar, status_text


def process_pitch(audio_path: Path, progress_bar, status_text) -> dict:
    """Process pitch through entire pipeline"""
    try:
        results = {}
        steps = [
            ("Loading and analyzing audio", 0.1),
            ("Extracting vocal features", 0.25),
            ("Transcribing speech", 0.45),
            ("Detecting emotions", 0.60),
            ("Analyzing transcript", 0.75),
            ("Generating scores", 0.85),
            ("Getting shark feedback", 0.95),
        ]
        
        # Step 1: Audio Processing
        status_text.text(steps[0][0])
        progress_bar.progress(int(steps[0][1] * 100))
        
        audio_processor = AudioProcessor()
        vocal_features = audio_processor.extract_all_vocal_features(audio_path)
        results['vocal_features'] = vocal_features
        
        # Step 2: Vocal Features (already extracted)
        status_text.text(steps[1][0])
        progress_bar.progress(int(steps[1][1] * 100))
        
        # Step 3: Transcription
        status_text.text(steps[2][0])
        progress_bar.progress(int(steps[2][1] * 100))
        
        transcription_engine = TranscriptionEngine()
        transcription = transcription_engine.transcribe(audio_path)
        results['transcription'] = transcription
        
        # Step 4: Emotion Analysis
        status_text.text(steps[3][0])
        progress_bar.progress(int(steps[3][1] * 100))
        
        emotion_analyzer = EmotionAnalyzer()
        emotion_analysis = emotion_analyzer.analyze_emotional_tone(
            audio_path,
            transcription['full_transcript']
        )
        results['emotion_analysis'] = emotion_analysis
        
        # Step 5: Transcript Analysis
        status_text.text(steps[4][0])
        progress_bar.progress(int(steps[4][1] * 100))
        
        transcript_analyzer = TranscriptAnalyzer()
        transcript_analysis = transcript_analyzer.analyze_transcript(
            transcription['full_transcript']
        )
        results['transcript_analysis'] = transcript_analysis
        
        # Step 6: Scoring
        status_text.text(steps[5][0])
        progress_bar.progress(int(steps[5][1] * 100))
        
        pitcher = PitchScorer()
        pitch_score = pitcher.score_pitch(
            vocal_features,
            emotion_analysis,
            transcript_analysis
        )
        results['pitch_score'] = pitch_score
        
        # Step 7: Feedback
        status_text.text(steps[6][0])
        progress_bar.progress(int(steps[6][1] * 100))
        
        feedback_engine = SharkPersonaFeedbackEngine()
        
        pitch_data = {
            'transcript': transcription['full_transcript'],
            'duration_seconds': vocal_features['duration_seconds'],
        }
        
        shark_feedback = feedback_engine.generate_all_feedback(
            pitch_data,
            pitch_score
        )
        results['shark_feedback'] = shark_feedback
        
        consensus = feedback_engine.generate_consensus_recommendation(shark_feedback)
        results['consensus'] = consensus
        
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        
        return results
    
    except Exception as e:
        logger.error(f"Error processing pitch: {e}")
        status_text.error(f"❌ Error: {str(e)}")
        raise


def display_results(results: dict):
    """Display comprehensive analysis results"""
    
    # Overall verdict
    pitch_score = results['pitch_score']
    overall_score = pitch_score['overall_score']
    verdict = pitch_score['verdict']
    
    # Determine verdict styling
    if verdict == "Invest":
        verdict_class = "verdict-invest"
        verdict_emoji = "✅"
    elif verdict == "Need More Info":
        verdict_class = "verdict-maybe"
        verdict_emoji = "⚠️"
    else:
        verdict_class = "verdict-no"
        verdict_emoji = "❌"
    
    st.markdown(f"""
    <div class="{verdict_class}">
        <h2>{verdict_emoji} {verdict}</h2>
        <h3>Overall Score: {overall_score:.1f}/10</h3>
        <p><em>{pitch_score['pitch_summary']}</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for different sections
    tabs = st.tabs([
        "📊 Scores",
        "🗣️ Transcript",
        "🦈 Shark Feedback",
        "🎵 Audio Analysis",
        "💭 Emotional Analysis"
    ])
    
    # Tab 1: Scores
    with tabs[0]:
        display_scores_tab(results)
    
    # Tab 2: Transcript
    with tabs[1]:
        display_transcript_tab(results)
    
    # Tab 2: Shark Feedback
    with tabs[2]:
        display_shark_feedback_tab(results)
    
    # Tab 4: Audio Analysis
    with tabs[3]:
        display_audio_analysis_tab(results)
    
    # Tab 5: Emotional Analysis
    with tabs[4]:
        display_emotion_analysis_tab(results)
    
    # Export results
    st.markdown("---")
    st.subheader("📥 Export Results")
    
    results_json = json.dumps(results, indent=2, default=str)
    st.download_button(
        label="Download Full Analysis (JSON)",
        data=results_json,
        file_name=f"pitch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )


def display_scores_tab(results: dict):
    """Display scoring metrics tab"""
    
    pitch_score = results['pitch_score']
    
    # Vocal Delivery Scores
    st.subheader("🎤 Vocal Delivery Scores")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Clarity",
            f"{pitch_score['vocal_delivery']['clarity']:.1f}/10",
            help="How clear and articulate is the speech?"
        )
    
    with col2:
        st.metric(
            "Energy",
            f"{pitch_score['vocal_delivery']['energy']:.1f}/10",
            help="How energetic and enthusiastic is the delivery?"
        )
    
    with col3:
        st.metric(
            "Confidence",
            f"{pitch_score['vocal_delivery']['confidence']:.1f}/10",
            help="How confident does the pitcher sound?"
        )
    
    with col4:
        st.metric(
            "Delivery Score",
            f"{pitch_score['vocal_delivery']['overall_score']:.1f}/10"
        )
    
    # Business Content Scores
    st.subheader("💼 Business Content Scores")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Problem",
            f"{pitch_score['business_content']['problem']:.1f}/10",
            help="Is the problem clearly articulated?"
        )
    
    with col2:
        st.metric(
            "Solution",
            f"{pitch_score['business_content']['solution']:.1f}/10",
            help="Is the solution well-explained?"
        )
    
    with col3:
        st.metric(
            "Market",
            f"{pitch_score['business_content']['market']:.1f}/10",
            help="Is market opportunity understood?"
        )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Revenue Model",
            f"{pitch_score['business_content']['revenue_model']:.1f}/10",
            help="Is the revenue model clear?"
        )
    
    with col2:
        st.metric(
            "Competition",
            f"{pitch_score['business_content']['competition']:.1f}/10",
            help="Competitive positioning"
        )
    
    with col3:
        st.metric(
            "Content Score",
            f"{pitch_score['business_content']['overall_score']:.1f}/10"
        )
    
    # Score breakdown
    st.subheader("Score Breakdown")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Vocal Delivery Weight: 50%**")
        st.write(f"Contribution: {pitch_score['vocal_delivery']['overall_score'] * 0.5:.1f}/10")
    
    with col2:
        st.write("**Business Content Weight: 50%**")
        st.write(f"Contribution: {pitch_score['business_content']['overall_score'] * 0.5:.1f}/10")


def display_transcript_tab(results: dict):
    """Display transcript analysis tab"""
    
    transcript_data = results['transcription']
    transcript_analysis = results['transcript_analysis']
    
    st.subheader("📝 Transcription")
    st.write(transcript_data['full_transcript'])
    
    st.markdown("---")
    st.subheader("📊 Transcript Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Word Count", transcript_data['word_count'])
    with col2:
        st.metric("Sentence Count", transcript_data.get('duration_seconds', 0))
    with col3:
        st.metric("Language", transcript_data['language'])
    with col4:
        st.metric("Confidence", f"{transcript_data.get('confidence', 0):.2f}")
    
    # Language complexity
    st.subheader("📖 Language Complexity")
    lang_metrics = transcript_analysis['language_metrics']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Avg Sentence Length",
            f"{lang_metrics['avg_sentence_length']:.1f} words"
        )
    with col2:
        st.metric(
            "Avg Word Length",
            f"{lang_metrics['avg_word_length']:.1f} chars"
        )
    with col3:
        st.metric(
            "Flesch Kincaid Grade",
            f"{lang_metrics['flesch_kincaid_grade']:.1f}"
        )
    with col4:
        st.metric(
            "Reading Ease",
            f"{lang_metrics['reading_ease']:.0f}/100"
        )
    
    # Key claims
    st.subheader("🎯 Key Claims")
    for i, claim in enumerate(transcript_analysis['key_claims'][:5], 1):
        st.markdown(f"{i}. {claim}")


def display_shark_feedback_tab(results: dict):
    """Display shark feedback tab"""
    
    st.subheader("🦈 Shark Panel Feedback")
    
    consensus = results['consensus']
    
    # Consensus verdict
    st.markdown(f"""
    ### Panel Consensus: {consensus['overall_verdict']}
    **Confidence Level:** {consensus['verdict_confidence']}
    
    {consensus['reasoning']}
    """)
    
    # Voting breakdown
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Strong Interest",
            f"{consensus['strong_interest_count']} shark(s)",
            f"{consensus['strong_interest_pct']:.0f}%"
        )
    
    with col2:
        st.metric(
            "Conditional Interest",
            f"{consensus['conditional_interest_count']} shark(s)",
            f"{consensus['conditional_interest_pct']:.0f}%"
        )
    
    with col3:
        st.metric(
            "Not Interested",
            f"{consensus['not_interested_count']} shark(s)",
            f"{consensus['not_interested_pct']:.0f}%"
        )
    
    # Individual shark feedback
    st.markdown("---")
    st.subheader("Individual Shark Feedback")
    
    for feedback in results['shark_feedback']:
        with st.expander(f"🦈 {feedback['persona']}"):
            st.write(f"**Archetype:** {feedback['archetype']}")
            st.write(f"**Focus Areas:** {', '.join(feedback['focus_areas'])}")
            st.write(f"**Tone:** {feedback['tone']}")
            st.write(f"**Recommendation:** {feedback['recommendation']}")
            st.markdown("---")
            st.write(feedback['feedback'])


def display_audio_analysis_tab(results: dict):
    """Display audio analysis tab"""
    
    vocal_features = results['vocal_features']
    
    st.subheader("🎵 Vocal Characteristics")
    
    # Pitch analysis
    st.markdown("#### Pitch Analysis")
    pitch_data = vocal_features['pitch']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Mean Pitch",
            f"{pitch_data['mean_pitch_hz']:.1f} Hz"
        )
    with col2:
        st.metric(
            "Pitch Std Dev",
            f"{pitch_data['std_pitch_hz']:.1f} Hz"
        )
    with col3:
        st.metric(
            "Pitch Range",
            f"{pitch_data['max_pitch_hz'] - pitch_data['min_pitch_hz']:.1f} Hz"
        )
    with col4:
        st.metric(
            "Voiced %",
            f"{pitch_data['voiced_percentage']:.1f}%"
        )
    
    # Volume analysis
    st.markdown("#### Volume & Energy")
    volume_data = vocal_features['volume']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("RMS Energy (Mean)", f"{volume_data['rms_energy_mean']:.4f}")
    with col2:
        st.metric("RMS Energy (Max)", f"{volume_data['rms_energy_max']:.4f}")
    with col3:
        st.metric("Dynamic Range", f"{volume_data['dynamic_range']:.4f}")
    with col4:
        st.metric("Spectral Energy", f"{volume_data['spectral_energy_mean']:.1f}")
    
    # Pace analysis
    st.markdown("#### Speech Pace")
    pace_data = vocal_features['pace']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Tempo (BPM)", f"{pace_data['tempo_bpm']:.1f}")
    with col2:
        st.metric("Onset Events", f"{pace_data['onset_count']}")
    with col3:
        st.metric("Spectral Centroid", f"{pace_data['spectral_centroid_mean']:.0f}")
    with col4:
        st.metric("Zero Crossing Rate", f"{pace_data['zero_crossing_rate']:.4f}")
    
    # Pause analysis
    st.markdown("#### Speech Pauses")
    pause_data = vocal_features['pauses']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Pause Count", f"{pause_data['pause_count']}")
    with col2:
        st.metric("Avg Pause Duration", f"{pause_data['avg_pause_duration']:.2f}s")
    with col3:
        st.metric("Total Pause Time", f"{pause_data['total_pause_duration']:.1f}s")
    with col4:
        st.metric("Pause Frequency", f"{pause_data['pause_frequency']:.2f}/s")


def display_emotion_analysis_tab(results: dict):
    """Display emotional analysis tab"""
    
    emotion_data = results['emotion_analysis']
    
    st.subheader("💭 Emotional Analysis")
    
    # Overall emotional state
    emotional_state = emotion_data['overall_emotional_state']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Emotional Intensity",
            f"{emotional_state['emotional_intensity']:.1f}/10"
        )
    
    with col2:
        st.metric(
            "Emotional Confidence",
            f"{emotional_state['emotional_confidence']:.1f}/10"
        )
    
    with col3:
        st.metric(
            "Emotional Alignment",
            emotional_state['emotional_alignment']
        )
    
    # Text emotions
    st.markdown("#### Detected Emotions (from text)")
    text_emotions = emotion_data['text_emotions']
    
    if text_emotions['emotion_distribution']:
        emotion_df = json.loads(json.dumps(text_emotions['emotion_distribution'], default=str))
        st.bar_chart(emotion_df)
    
    st.markdown(f"**Dominant Emotion:** {text_emotions['dominant_emotion'].title()}")
    st.markdown(f"**Confidence:** {text_emotions['dominant_emotion_score']:.2%}")


def main():
    """Main application flow"""
    
    initialize_session_state()
    display_header()
    
    st.markdown("""
    Welcome to the Shark Tank Pitch Analyzer! Upload your pitch audio and get:
    - 🎤 Vocal delivery analysis (clarity, energy, confidence)
    - 💼 Business content scoring (problem, solution, market, revenue model, competition)
    - 🦈 Multi-shark feedback from different investor perspectives
    - 📊 Detailed metrics and recommendations
    """)
    
    # Upload section
    uploaded_file = display_upload_section()
    
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        
        # Validate file
        temp_audio_path = save_uploaded_file(uploaded_file)
        is_valid, validation_message = validate_and_process_audio(temp_audio_path)
        
        if is_valid:
            st.success(validation_message)
            
            # Process button
            if st.button("🚀 Analyze Pitch", use_container_width=True, type="primary"):
                st.session_state.processing = True
                
                status_container = st.container()
                progress_bar, status_text = display_processing_status(status_container)
                
                try:
                    results = process_pitch(temp_audio_path, progress_bar, status_text)
                    st.session_state.analysis_results = results
                    st.session_state.analysis_complete = True
                    st.success("✅ Analysis complete!")
                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")
                    logger.error(f"Analysis error: {e}", exc_info=True)
                finally:
                    st.session_state.processing = False
            
            # Display results if available
            if st.session_state.analysis_complete and st.session_state.analysis_results:
                st.markdown("---")
                display_results(st.session_state.analysis_results)
        
        else:
            st.error(f"❌ {validation_message}")
    
    # Sidebar info
    with st.sidebar:
        st.markdown("## 📋 About")
        st.markdown("""
        **Shark Tank Pitch Analyzer** uses AI to evaluate your pitch across multiple dimensions:
        
        - **Audio Processing:** Librosa
        - **Speech Recognition:** OpenAI Whisper
        - **NLP Analysis:** spaCy, NLTK, Transformers
        - **Emotion Detection:** openSMILE, Transformers
        - **LLM Feedback:** LangChain + Hugging Face
        - **UI:** Streamlit
        
        Upload a 30-second to 10-minute pitch audio and get instant feedback!
        """)
        
        st.markdown("---")
        st.markdown("## 🦈 Shark Personas")
        for persona_key, persona in {
            'strategic_investor': 'Strategic Investor',
            'finance_expert': 'Finance Expert',
            'product_visionary': 'Product Visionary',
            'domain_expert': 'Domain Expert',
            'aggressive_dealer': 'Aggressive Dealer',
        }.items():
            st.markdown(f"- {persona}")


if __name__ == "__main__":
    main()
