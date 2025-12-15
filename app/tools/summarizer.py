from typing import Dict, Any, Optional
from .gemini_text import GeminiTextTool


class SummarizerTool:
    def __init__(self, gemini_tool: Optional[GeminiTextTool] = None):
        self.gemini_tool = gemini_tool or GeminiTextTool()
    
    def summarize(self, text: str) -> Dict[str, Any]:
        if "\n\nYouTube video transcript:\n" in text:
            parts = text.split("\n\nYouTube video transcript:\n", 1)
            user_prompt = parts[0].strip()
            if "youtube-transcript-api" in user_prompt.lower():
                if "The following text is the transcript" in user_prompt:
                    user_prompt = user_prompt.split("The following text is the transcript")[0].strip()
            content = parts[1] if len(parts) > 1 else text
            instruction = user_prompt if "summar" in user_prompt.lower() else "Summarize the following YouTube video transcript"
        elif "\n\nTranscribed audio content:\n" in text:
            parts = text.split("\n\nTranscribed audio content:\n", 1)
            user_prompt = parts[0].strip()
            content = parts[1] if len(parts) > 1 else text
            instruction = user_prompt if "summar" in user_prompt.lower() else "Summarize the following"
        elif "\n\nExtracted PDF content:\n" in text:
            parts = text.split("\n\nExtracted PDF content:\n", 1)
            user_prompt = parts[0].strip()
            if "using Python packages" in user_prompt:
                user_prompt = user_prompt.split("using Python packages")[0].strip()
            content = parts[1] if len(parts) > 1 else text
            instruction = user_prompt if "summar" in user_prompt.lower() else "Summarize the following PDF content"
        elif "Image analysis and content:\n" in text or "\n\nExtracted image text:\n" in text or "extracted from an image using OCR" in text.lower() or "Image Description:" in text:
            if "Image analysis and content:\n" in text:
                parts = text.split("Image analysis and content:\n", 1)
            elif "\n\nExtracted image text:\n" in text:
                parts = text.split("\n\nExtracted image text:\n", 1)
            else:
                parts = text.split("Extracted image text:\n", 1)
            user_prompt = parts[0].strip()
            if "The following text was extracted from an image" in user_prompt:
                user_prompt = user_prompt.split("The following text was extracted from an image")[0].strip()
            if "An image was uploaded and analyzed" in user_prompt:
                user_prompt = user_prompt.split("An image was uploaded and analyzed")[0].strip()
            content = parts[1] if len(parts) > 1 else text
            instruction = user_prompt if "summar" in user_prompt.lower() else "Summarize the following image content"
        else:
            instruction = "Summarize the following"
            content = text
        
        prompt = f"""{instruction} text in EXACTLY this format:

1. ONE-LINE SUMMARY:
[One sentence summary]

2. KEY POINTS:
- [First key point]
- [Second key point]
- [Third key point]

3. DETAILED SUMMARY:
[Sentence 1]
[Sentence 2]
[Sentence 3]
[Sentence 4]
[Sentence 5]

Text to summarize:
{content[:5000]}
"""
        
        response = self.gemini_tool.generate(prompt)
        
        if response.get("error"):
            return {
                "summary": None,
                "error": response["error"],
                "success": False,
                "metadata": {}
            }
        
        return {
            "summary": response["text"],
            "success": True,
            "metadata": {
                "input_length": len(text),
                "method": "gemini"
            }
        }
