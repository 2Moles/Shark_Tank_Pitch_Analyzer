"""Multi-Agent Feedback Engine using LangChain and Hugging Face LLMs"""

import logging
from typing import Dict, List, Any
from config import SHARK_PERSONAS, LLM_MODEL, LLM_MAX_TOKENS, LLM_TEMPERATURE

logger = logging.getLogger(__name__)


class SharkPersonaFeedbackEngine:
    """
    Generates multi-persona feedback using LangChain and Hugging Face LLMs.
    Each shark provides perspective based on their archetype and focus areas.
    """
    
    def __init__(self):
        """Initialize feedback engine with shark personas"""
        self.personas = SHARK_PERSONAS
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self) -> None:
        """Initialize Hugging Face LLM through LangChain"""
        try:
            logger.info(f"Initializing LLM: {LLM_MODEL}")
            
            try:
                from langchain_community.llms import HuggingFaceHub
                from langchain.prompts import PromptTemplate
                from langchain.chains import LLMChain
                
                # Initialize Hugging Face LLM
                self.llm = HuggingFaceHub(
                    repo_id=LLM_MODEL,
                    model_kwargs={
                        "temperature": LLM_TEMPERATURE,
                        "max_length": LLM_MAX_TOKENS,
                    },
                    task="text-generation",
                )
                
                logger.info("LLM initialized successfully")
            
            except ImportError:
                logger.warning("LangChain Hugging Face integration not available, using fallback")
                self.llm = None
        
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            self.llm = None
    
    def generate_persona_feedback(
        self,
        persona_key: str,
        pitch_data: Dict[str, Any],
        scores: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate feedback from a specific shark persona
        
        Args:
            persona_key: Key of the persona (strategic_investor, finance_expert, etc.)
            pitch_data: Original pitch data (transcript, duration, etc.)
            scores: Calculated scores (vocal, content, overall)
        
        Returns:
            Dictionary with persona feedback
        """
        try:
            persona = self.personas.get(persona_key)
            if not persona:
                raise ValueError(f"Unknown persona: {persona_key}")
            
            logger.info(f"Generating feedback from {persona['name']}...")
            
            # Build context for the persona
            feedback_prompt = self._build_feedback_prompt(persona, pitch_data, scores)
            
            # Generate feedback
            feedback_text = self._generate_feedback_text(feedback_prompt)
            
            # Structure the response
            persona_feedback = {
                'persona': persona['name'],
                'archetype': persona['archetype'],
                'focus_areas': persona['focus_areas'],
                'tone': persona['tone'],
                'feedback': feedback_text,
                'key_points': self._extract_key_points(feedback_text, persona),
                'recommendation': self._extract_recommendation(feedback_text),
            }
            
            logger.info(f"Feedback generated from {persona['name']}")
            return persona_feedback
        
        except Exception as e:
            logger.error(f"Error generating persona feedback: {e}")
            return self._get_default_persona_feedback(persona_key)
    
    def _build_feedback_prompt(
        self,
        persona: Dict[str, Any],
        pitch_data: Dict[str, Any],
        scores: Dict[str, Any]
    ) -> str:
        """
        Build prompt for LLM to generate persona-specific feedback
        
        Args:
            persona: Shark persona configuration
            pitch_data: Pitch information
            scores: Calculated scores
        
        Returns:
            Formatted prompt string
        """
        transcript = pitch_data.get('transcript', '')[:500]  # First 500 chars
        duration = pitch_data.get('duration_seconds', 0)
        
        vocal_score = scores.get('vocal_delivery', {}).get('overall_score', 0)
        content_score = scores.get('business_content', {}).get('overall_score', 0)
        overall_score = scores.get('overall_score', 0)
        
        prompt = f"""You are {persona['name']}, a {persona['archetype']}.
You evaluate pitches with a focus on: {', '.join(persona['focus_areas'])}.
Your communication style is: {persona['tone']}.

A pitcher just delivered a {duration:.0f}-second pitch. Here's what you noticed:

PITCH EXCERPT:
"{transcript}"

PERFORMANCE SCORES:
- Vocal Delivery: {vocal_score:.1f}/10
- Business Content: {content_score:.1f}/10
- Overall Score: {overall_score:.1f}/10

Provide your honest, persona-specific feedback on this pitch. Focus on the aspects that matter to you most.
Highlight strengths, weaknesses, and what would convince you to invest or not.
Keep it concise and in your characteristic tone.

Your feedback:"""
        
        return prompt
    
    def _generate_feedback_text(self, prompt: str) -> str:
        """
        Generate feedback text using LLM
        
        Args:
            prompt: Formatted prompt for LLM
        
        Returns:
            Generated feedback text
        """
        try:
            if self.llm:
                logger.info("Generating feedback with LLM...")
                response = self.llm(prompt)
                # Clean up response
                feedback = response.strip()
                # Limit length
                if len(feedback) > 1000:
                    feedback = feedback[:1000].rsplit(' ', 1)[0] + "..."
                return feedback
            else:
                # Fallback: generate template-based feedback
                return self._generate_template_feedback(prompt)
        
        except Exception as e:
            logger.error(f"Error generating feedback with LLM: {e}")
            return self._generate_template_feedback(prompt)
    
    def _generate_template_feedback(self, prompt: str) -> str:
        """
        Generate template-based feedback as fallback
        
        Args:
            prompt: The prompt containing pitch data
        
        Returns:
            Generated feedback
        """
        try:
            # Extract scores from prompt
            import re
            
            vocal_match = re.search(r"Vocal Delivery: ([\d.]+)", prompt)
            content_match = re.search(r"Business Content: ([\d.]+)", prompt)
            overall_match = re.search(r"Overall Score: ([\d.]+)", prompt)
            
            vocal_score = float(vocal_match.group(1)) if vocal_match else 5
            content_score = float(content_match.group(1)) if content_match else 5
            overall_score = float(overall_match.group(1)) if overall_match else 5
            
            # Generate feedback based on scores
            feedback_parts = []
            
            if vocal_score > 7:
                feedback_parts.append("Your delivery is strong and confident.")
            elif vocal_score > 5:
                feedback_parts.append("Your delivery is decent but could use more energy.")
            else:
                feedback_parts.append("Your delivery needs work - focus on clarity and energy.")
            
            if content_score > 7:
                feedback_parts.append("The business proposition is solid.")
            elif content_score > 5:
                feedback_parts.append("The business model needs more clarity.")
            else:
                feedback_parts.append("The business idea requires significant development.")
            
            if overall_score > 7:
                feedback_parts.append("This is a promising pitch worth exploring further.")
            elif overall_score > 5:
                feedback_parts.append("There's potential here, but you need to address some concerns.")
            else:
                feedback_parts.append("This pitch needs more work before I'd consider investing.")
            
            return " ".join(feedback_parts)
        
        except Exception as e:
            logger.error(f"Error in template feedback: {e}")
            return "This is an interesting pitch with both strengths and areas for improvement."
    
    def _extract_key_points(self, feedback_text: str, persona: Dict[str, Any]) -> List[str]:
        """
        Extract key points from feedback
        
        Args:
            feedback_text: Generated feedback
            persona: Persona information
        
        Returns:
            List of key points
        """
        try:
            # Split into sentences
            sentences = [s.strip() for s in feedback_text.split('.') if s.strip()]
            # Return first 3 substantial sentences
            return sentences[:3]
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            return []
    
    def _extract_recommendation(self, feedback_text: str) -> str:
        """
        Extract investment recommendation from feedback
        
        Args:
            feedback_text: Generated feedback
        
        Returns:
            Recommendation string
        """
        try:
            feedback_lower = feedback_text.lower()
            
            if any(word in feedback_lower for word in ['invest', 'yes', 'definitely', 'strong', 'promising']):
                return "Strong Interest"
            elif any(word in feedback_lower for word in ['maybe', 'possibly', 'could work', 'potential', 'revisit']):
                return "Conditional Interest"
            elif any(word in feedback_lower for word in ['no', 'not interested', 'pass', 'needs work', 'lacks']):
                return "Not Interested"
            else:
                return "Undecided"
        
        except Exception as e:
            logger.error(f"Error extracting recommendation: {e}")
            return "Undecided"
    
    def generate_all_feedback(
        self,
        pitch_data: Dict[str, Any],
        scores: Dict[str, Any],
        selected_personas: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate feedback from all or selected shark personas
        
        Args:
            pitch_data: Original pitch data
            scores: Calculated scores
            selected_personas: List of persona keys to include (None = all)
        
        Returns:
            List of persona feedback dictionaries
        """
        try:
            logger.info("Generating feedback from all shark personas...")
            
            personas_to_use = selected_personas or list(self.personas.keys())
            all_feedback = []
            
            for persona_key in personas_to_use:
                if persona_key in self.personas:
                    persona_feedback = self.generate_persona_feedback(
                        persona_key,
                        pitch_data,
                        scores
                    )
                    all_feedback.append(persona_feedback)
            
            logger.info(f"Generated feedback from {len(all_feedback)} personas")
            return all_feedback
        
        except Exception as e:
            logger.error(f"Error generating all feedback: {e}")
            return []
    
    def generate_consensus_recommendation(self, all_feedback: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate consensus recommendation from all personas
        
        Args:
            all_feedback: List of persona feedback
        
        Returns:
            Dictionary with consensus analysis
        """
        try:
            logger.info("Generating consensus recommendation...")
            
            if not all_feedback:
                return self._get_default_consensus()
            
            # Count recommendations
            recommendations = {}
            for feedback in all_feedback:
                rec = feedback.get('recommendation', 'Undecided')
                recommendations[rec] = recommendations.get(rec, 0) + 1
            
            # Determine consensus
            total_sharks = len(all_feedback)
            strong_interest = recommendations.get('Strong Interest', 0)
            conditional_interest = recommendations.get('Conditional Interest', 0)
            not_interested = recommendations.get('Not Interested', 0)
            
            # Calculate percentages
            strong_pct = (strong_interest / total_sharks) * 100
            conditional_pct = (conditional_interest / total_sharks) * 100
            not_pct = (not_interested / total_sharks) * 100
            
            # Determine overall verdict
            if strong_pct >= 60:
                overall_verdict = "Go For It!"
                verdict_confidence = "High"
            elif strong_pct >= 40:
                overall_verdict = "Worth Considering"
                verdict_confidence = "Medium"
            else:
                overall_verdict = "Needs Improvement"
                verdict_confidence = "Low" if not_pct >= 60 else "Mixed"
            
            consensus = {
                'overall_verdict': overall_verdict,
                'verdict_confidence': verdict_confidence,
                'strong_interest_count': strong_interest,
                'conditional_interest_count': conditional_interest,
                'not_interested_count': not_interested,
                'strong_interest_pct': strong_pct,
                'conditional_interest_pct': conditional_pct,
                'not_interested_pct': not_pct,
                'reasoning': self._generate_consensus_reasoning(
                    strong_pct, conditional_pct, not_pct
                ),
            }
            
            logger.info(f"Consensus verdict: {overall_verdict}")
            return consensus
        
        except Exception as e:
            logger.error(f"Error generating consensus: {e}")
            return self._get_default_consensus()
    
    def _generate_consensus_reasoning(self, strong_pct: float, conditional_pct: float, not_pct: float) -> str:
        """Generate reasoning for consensus verdict"""
        parts = []
        
        if strong_pct > conditional_pct and strong_pct > not_pct:
            parts.append(f"{int(strong_pct)}% of sharks showed strong interest.")
            if conditional_pct > 0:
                parts.append(f"Some ({int(conditional_pct)}%) would consider it with certain conditions.")
        elif conditional_pct > strong_pct and conditional_pct > not_pct:
            parts.append(f"{int(conditional_pct)}% of sharks are conditionally interested.")
            parts.append("The pitch has potential but needs refinement.")
        else:
            parts.append(f"Most sharks ({int(not_pct)}%) are not interested at this time.")
        
        return " ".join(parts)
    
    @staticmethod
    def _get_default_persona_feedback(persona_key: str) -> Dict[str, Any]:
        """Return default persona feedback"""
        return {
            'persona': persona_key,
            'archetype': 'Unknown',
            'focus_areas': [],
            'tone': 'professional',
            'feedback': 'Unable to generate detailed feedback at this time.',
            'key_points': [],
            'recommendation': 'Undecided',
        }
    
    @staticmethod
    def _get_default_consensus() -> Dict[str, Any]:
        """Return default consensus"""
        return {
            'overall_verdict': 'Unable to determine',
            'verdict_confidence': 'Low',
            'strong_interest_count': 0,
            'conditional_interest_count': 0,
            'not_interested_count': 0,
            'strong_interest_pct': 0,
            'conditional_interest_pct': 0,
            'not_interested_pct': 0,
            'reasoning': 'Unable to generate consensus at this time.',
        }
