import os
import google.generativeai as genai
from typing import Dict, Any, Optional
from PIL import Image
from app.config import GOOGLE_API_KEY


class GeminiVisionTool:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY") or GOOGLE_API_KEY
        if not self.api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found. Please set it as an environment variable or in a .env file. "
                "Get your API key from: https://makersuite.google.com/app/apikey"
            )
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-flash-latest')
    
    def extract_text_from_image(self, image_path: str) -> Dict[str, Any]:
        try:
            img = Image.open(image_path)
            prompt = "Extract all text from this image. Return only the extracted text, no explanations."
            response = self.model.generate_content([prompt, img])
            
            extracted_text = response.text.strip() if response.text else ""
            confidence = min(0.95, 0.5 + (len(extracted_text) / 1000) * 0.3) if extracted_text else 0.0
            
            return {
                "text": extracted_text,
                "confidence": confidence,
                "metadata": {
                    "model": "gemini-flash-latest",
                    "image_size": img.size,
                    "method": "gemini_vision"
                },
                "success": True
            }
        except Exception as e:
            return {
                "text": None,
                "confidence": 0.0,
                "error": str(e),
                "success": False,
                "metadata": {}
            }
    
    def analyze_image(self, image_path: str, query: Optional[str] = None) -> Dict[str, Any]:
        try:
            img = Image.open(image_path)
            prompt = query or "Describe what you see in this image in detail."
            response = self.model.generate_content([prompt, img])
            
            return {
                "text": response.text,
                "metadata": {
                    "model": "gemini-flash-latest",
                    "query": query
                },
                "success": True
            }
        except Exception as e:
            return {
                "text": None,
                "error": str(e),
                "success": False,
                "metadata": {}
            }
