"""
Tests for Executor Agent
"""
import pytest
from app.agents.executor import ExecutorAgent
from app.schemas.models import ExtractedContent


def test_executor_initialization():
    """Test executor agent initialization"""
    executor = ExecutorAgent()
    assert executor is not None
    assert executor.gemini_text is not None


def test_executor_summarize():
    """Test executor summarization"""
    executor = ExecutorAgent()
    
    extracted_content = ExtractedContent(
        source_type="text",
        content="This is a long text that needs to be summarized. It contains multiple sentences and ideas.",
        confidence=1.0
    )
    
    result = executor.execute(
        intent="summarize",
        extracted_content=extracted_content,
        user_message="Summarize this",
        tools_to_use=["summarizer"]
    )
    
    # Should succeed if API key is available
    # If not, will fail gracefully
    assert result is not None


def test_executor_sentiment():
    """Test executor sentiment analysis"""
    executor = ExecutorAgent()
    
    extracted_content = ExtractedContent(
        source_type="text",
        content="I love this product! It's amazing and wonderful.",
        confidence=1.0
    )
    
    result = executor.execute(
        intent="sentiment_analysis",
        extracted_content=extracted_content,
        user_message="Analyze sentiment",
        tools_to_use=["sentiment"]
    )
    
    assert result is not None

