from typing import Dict, Any, Optional
from app.tools.gemini_text import GeminiTextTool
from app.schemas.models import IntentDetection, PlannerDecision


class PlannerAgent:
    def __init__(self, gemini_tool: Optional[GeminiTextTool] = None):
        self.gemini_tool = gemini_tool or GeminiTextTool()
    
    def analyze(self, user_message: str, extracted_content: Optional[str] = None) -> Dict[str, Any]:
        intent_result = self.gemini_tool.detect_intent(user_message, extracted_content)
        
        # Handle short follow-up questions when we have extracted content
        if extracted_content and len(user_message.strip().split()) <= 3:
            intent_result["intent"] = "qa"
            intent_result["confidence"] = 0.9
            intent_result["is_ambiguous"] = False
            intent_result["clarification_needed"] = False
        
        intent_detection = IntentDetection(
            intent=intent_result.get("intent", "unknown"),
            confidence=intent_result.get("confidence", 0.0),
            is_ambiguous=intent_result.get("is_ambiguous", True),
            constraints=intent_result.get("constraints", {}),
            clarification_needed=intent_result.get("clarification_needed", True),
            clarification_question=intent_result.get("clarification_question")
        )
        
        planner_decision = self._make_decision(intent_detection, user_message, extracted_content)
        
        return {
            "intent_detection": intent_detection,
            "planner_decision": planner_decision
        }
    
    def _make_decision(self, intent_detection: IntentDetection, user_message: str, extracted_content: Optional[str]) -> PlannerDecision:
        # If we have extracted content from file upload, treat follow-ups as Q&A
        if extracted_content and extracted_content.strip():
            if intent_detection.intent == "unknown" or intent_detection.is_ambiguous:
                return PlannerDecision(
                    should_proceed=True,
                    reasoning="Follow-up question about uploaded content. Proceeding with Q&A intent.",
                    planned_steps=[
                        "Use Gemini to answer question about the uploaded content",
                        "Provide response based on extracted content"
                    ],
                    tools_to_use=["gemini_text"],
                    clarification_question=None
                )
        
        # Don't proceed if intent is ambiguous (except for Q&A which is more flexible)
        if intent_detection.clarification_needed or (intent_detection.is_ambiguous and intent_detection.intent != "qa"):
            return PlannerDecision(
                should_proceed=False,
                reasoning=f"Intent is ambiguous (confidence: {intent_detection.confidence:.2f}). Clarification needed.",
                planned_steps=[],
                tools_to_use=[],
                clarification_question=intent_detection.clarification_question or "Could you clarify what you'd like me to do?"
            )
        
        # Map intent to tools
        intent = intent_detection.intent
        tools_to_use = []
        planned_steps = []
        
        if intent == "extract_text":
            planned_steps = ["Return extracted text"]
            tools_to_use = []
        elif intent == "summarize":
            planned_steps = [
                "Use Gemini to generate summary",
                "Format output: 1-line summary, 3 bullet points, 5-sentence paragraph"
            ]
            tools_to_use = ["summarizer"]
        elif intent == "sentiment_analysis":
            planned_steps = [
                "Use Gemini to analyze sentiment",
                "Return sentiment label, confidence, and justification"
            ]
            tools_to_use = ["sentiment"]
        elif intent == "code_explanation":
            planned_steps = [
                "Use Gemini to explain code",
                "Detect bugs and risks",
                "Analyze time complexity"
            ]
            tools_to_use = ["code_explainer"]
        elif intent == "transcription":
            planned_steps = ["Return transcription result"]
            tools_to_use = []
        elif intent == "qa":
            planned_steps = [
                "Use Gemini to answer question",
                "Provide factual, friendly response"
            ]
            tools_to_use = ["gemini_text"]
        else:
            return PlannerDecision(
                should_proceed=False,
                reasoning=f"Unknown intent: {intent}",
                planned_steps=[],
                tools_to_use=[],
                clarification_question="Could you clarify what you'd like me to do?"
            )
        
        return PlannerDecision(
            should_proceed=True,
            reasoning=f"Intent '{intent}' is clear (confidence: {intent_detection.confidence:.2f}). Proceeding with execution.",
            planned_steps=planned_steps,
            tools_to_use=tools_to_use,
            clarification_question=None
        )
