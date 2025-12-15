import os
import google.generativeai as genai
from typing import Dict, Any, Optional
from app.config import GOOGLE_API_KEY


class GeminiTextTool:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or GOOGLE_API_KEY
        if not self.api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found. Please set it as an environment variable or in a .env file. "
                "Get your API key from: https://makersuite.google.com/app/apikey"
            )
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-flash-latest')
    
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        try:
            response = self.model.generate_content(prompt, **kwargs)
            if response and hasattr(response, 'text') and response.text:
                finish_reason = None
                if response.candidates:
                    finish_reason = getattr(response.candidates[0].finish_reason, 'name', 'UNKNOWN')
                return {
                    "text": response.text,
                    "metadata": {
                        "model": "gemini-flash-latest",
                        "finish_reason": finish_reason
                    }
                }
            else:
                return {
                    "text": None,
                    "error": "Empty response from Gemini API",
                    "metadata": {}
                }
        except Exception as e:
            return {
                "text": None,
                "error": str(e),
                "metadata": {}
            }
    
    def detect_intent(self, user_message: str, extracted_content: Optional[str] = None) -> Dict[str, Any]:
        context = f"User message: {user_message}\n"
        if extracted_content:
            context += f"Extracted content preview (first 500 chars): {extracted_content[:500]}\n"
        
        prompt = f"""Analyze the following user request and determine:
1. What is the user's primary intent? (e.g., summarize, extract_text, sentiment_analysis, code_explanation, transcription, qa)
2. Is the intent clear or ambiguous?
3. Are there any constraints mentioned? (format, length, specific instructions)
4. Does this require clarification before proceeding?

{context}

Respond in JSON format:
{{
    "intent": "string (one of: summarize, extract_text, sentiment_analysis, code_explanation, transcription, qa, unknown)",
    "confidence": float (0-1),
    "is_ambiguous": boolean,
    "constraints": {{"format": "...", "length": "...", "instruction": "..."}},
    "clarification_needed": boolean,
    "clarification_question": "string or null"
}}"""
        
        response = self.generate(prompt)
        if response.get("error"):
            return self._parse_intent_fallback(user_message)
        
        try:
            import json
            text = response["text"]
            if not text:
                return self._parse_intent_fallback(user_message)
            
            start_idx = text.find("{")
            end_idx = text.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = text[start_idx:end_idx]
                result = json.loads(json_str)
                if result.get("intent") and result.get("intent") != "unknown":
                    return result
                else:
                    return self._parse_intent_fallback(user_message)
            else:
                return self._parse_intent_fallback(user_message)
        except Exception as e:
            return self._parse_intent_fallback(user_message)
    
    def _parse_intent_fallback(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower().strip()
        
        greetings = ["hi", "hello", "hey", "greetings", "how are you", "what's up", "how do you do"]
        if any(greeting in text_lower for greeting in greetings) and len(text_lower.split()) <= 5:
            return {
                "intent": "qa",
                "confidence": 0.9,
                "is_ambiguous": False,
                "constraints": {},
                "clarification_needed": False,
                "clarification_question": None
            }
        
        if any(word in text_lower for word in ["summarize", "summary", "summarise"]):
            intent = "summarize"
            confidence = 0.7
        elif any(word in text_lower for word in ["sentiment", "feeling", "emotion"]):
            intent = "sentiment_analysis"
            confidence = 0.7
        elif any(word in text_lower for word in ["explain", "code", "function", "bug"]):
            intent = "code_explanation"
            confidence = 0.7
        elif any(word in text_lower for word in ["extract", "text", "ocr"]):
            intent = "extract_text"
            confidence = 0.7
        elif any(word in text_lower for word in ["transcribe", "transcription", "audio"]):
            intent = "transcription"
            confidence = 0.7
        else:
            intent = "qa"
            confidence = 0.8
        
        return {
            "intent": intent,
            "confidence": confidence,
            "is_ambiguous": False,
            "constraints": {},
            "clarification_needed": False,
            "clarification_question": None
        }
