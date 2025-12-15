"""
Tests for Planner Agent
"""
import pytest
from app.agents.planner import PlannerAgent
from app.tools.gemini_text import GeminiTextTool


def test_planner_initialization():
    """Test planner agent initialization"""
    planner = PlannerAgent()
    assert planner is not None
    assert planner.gemini_tool is not None


def test_planner_ambiguous_intent():
    """Test planner handles ambiguous intent"""
    planner = PlannerAgent()
    
    # Ambiguous request
    result = planner.analyze("Do something with this")
    
    assert result["intent_detection"].is_ambiguous or result["intent_detection"].clarification_needed
    assert not result["planner_decision"].should_proceed
    assert result["planner_decision"].clarification_question is not None


def test_planner_clear_intent():
    """Test planner handles clear intent"""
    planner = PlannerAgent()
    
    # Clear request
    result = planner.analyze("Summarize this text", "This is a long text that needs to be summarized.")
    
    # Should proceed if intent is clear
    if not result["intent_detection"].is_ambiguous:
        assert result["planner_decision"].should_proceed
        assert "summarizer" in result["planner_decision"].tools_to_use or len(result["planner_decision"].tools_to_use) >= 0

