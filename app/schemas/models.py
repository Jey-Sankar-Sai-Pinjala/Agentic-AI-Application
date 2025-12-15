from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ExtractedContent(BaseModel):
    source_type: Literal["text", "image", "pdf", "audio", "youtube"]
    content: str
    confidence: Optional[float] = None
    metadata: Dict[str, Any] = {}


class IntentDetection(BaseModel):
    intent: str
    confidence: float = Field(ge=0.0, le=1.0)
    is_ambiguous: bool
    constraints: Dict[str, Any] = {}
    clarification_needed: bool
    clarification_question: Optional[str] = None


class ToolUsage(BaseModel):
    tool_name: str
    tool_type: Literal["gemini_text", "gemini_vision", "pdf_parser", "ocr", "whisper", "youtube", "summarizer", "sentiment", "code_explainer"]
    success: bool
    fallback_used: bool = False
    execution_time: Optional[float] = None


class PlannerDecision(BaseModel):
    should_proceed: bool
    reasoning: str
    planned_steps: List[str] = []
    tools_to_use: List[str] = []
    clarification_question: Optional[str] = None


class ExecutionResult(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None
    tools_used: List[ToolUsage] = []


class ChatRequest(BaseModel):
    message: str
    file_path: Optional[str] = None
    file_type: Optional[Literal["image", "pdf", "audio"]] = None
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    extracted_content: Optional[ExtractedContent] = None
    intent_detection: IntentDetection
    planner_decision: PlannerDecision
    execution_result: Optional[ExecutionResult] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    session_id: Optional[str] = None

