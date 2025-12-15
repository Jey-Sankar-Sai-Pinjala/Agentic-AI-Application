from typing import Dict, Any, Optional
from .gemini_text import GeminiTextTool


class CodeExplainerTool:
    def __init__(self, gemini_tool: Optional[GeminiTextTool] = None):
        self.gemini_tool = gemini_tool or GeminiTextTool()
    
    def explain_code(self, code: str, language: Optional[str] = None) -> Dict[str, Any]:
        prompt = f"""Analyze the following code and provide:
1. Explanation of functionality
2. Any bugs or potential issues
3. Security risks or concerns
4. Time complexity analysis

Code:
{code[:3000]}

Respond in this format:
FUNCTIONALITY:
[Explanation]

BUGS/ISSUES:
[List any bugs or issues, or "None detected"]

RISKS:
[List any security or performance risks, or "None detected"]

TIME COMPLEXITY:
[Analysis of time complexity]
"""
        
        response = self.gemini_tool.generate(prompt)
        
        if response.get("error"):
            return {
                "explanation": None,
                "bugs": None,
                "risks": None,
                "time_complexity": None,
                "error": response["error"],
                "success": False,
                "metadata": {}
            }
        
        return {
            "explanation": response["text"],
            "success": True,
            "metadata": {
                "code_length": len(code),
                "language": language or "unknown",
                "method": "gemini"
            }
        }
