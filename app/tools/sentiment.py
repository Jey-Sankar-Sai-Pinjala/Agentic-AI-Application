from typing import Dict, Any, Optional
from .gemini_text import GeminiTextTool


class SentimentTool:
    def __init__(self, gemini_tool: Optional[GeminiTextTool] = None):
        self.gemini_tool = gemini_tool or GeminiTextTool()
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        prompt = f"""Analyze the sentiment of the following text and respond in JSON format:
{{
    "sentiment": "positive" | "negative" | "neutral",
    "confidence": float (0-1),
    "justification": "one-line explanation"
}}

Text:
{text[:2000]}
"""
        
        response = self.gemini_tool.generate(prompt)
        
        if response.get("error"):
            return {
                "sentiment": None,
                "confidence": 0.0,
                "justification": None,
                "error": response["error"],
                "success": False,
                "metadata": {}
            }
        
        try:
            import json
            response_text = response["text"]
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                result = json.loads(json_str)
                return {
                    "sentiment": result.get("sentiment", "neutral"),
                    "confidence": float(result.get("confidence", 0.5)),
                    "justification": result.get("justification", "Unable to determine"),
                    "success": True,
                    "metadata": {"method": "gemini"}
                }
        except Exception:
            pass
        
        # Fallback: simple keyword-based sentiment
        text_lower = text.lower()
        positive_words = ["good", "great", "excellent", "happy", "love", "wonderful", "amazing"]
        negative_words = ["bad", "terrible", "awful", "hate", "sad", "horrible", "disappointed"]
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            sentiment = "positive"
            confidence = min(0.8, 0.5 + pos_count * 0.1)
        elif neg_count > pos_count:
            sentiment = "negative"
            confidence = min(0.8, 0.5 + neg_count * 0.1)
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "justification": f"Based on keyword analysis: {pos_count} positive, {neg_count} negative indicators",
            "success": True,
            "metadata": {"method": "fallback_keywords"}
        }
