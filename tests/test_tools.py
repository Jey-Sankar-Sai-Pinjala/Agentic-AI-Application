"""
Tests for tools
"""
import pytest
import os


def test_youtube_tool():
    """Test YouTube tool video ID extraction"""
    from app.tools.youtube import YouTubeTool
    
    tool = YouTubeTool()
    
    # Test URL extraction
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    video_id = tool.extract_video_id(url)
    assert video_id == "dQw4w9WgXcQ"
    
    url2 = "https://youtu.be/dQw4w9WgXcQ"
    video_id2 = tool.extract_video_id(url2)
    assert video_id2 == "dQw4w9WgXcQ"


def test_pdf_parser_initialization():
    """Test PDF parser initialization"""
    from app.tools.pdf_parser import PDFParserTool
    
    tool = PDFParserTool()
    assert tool is not None


def test_ocr_initialization():
    """Test OCR tool initialization"""
    from app.tools.ocr import OCRTool
    
    tool = OCRTool()
    assert tool is not None


def test_audio_whisper_initialization():
    """Test Audio Whisper tool initialization"""
    from app.tools.audio_whisper import AudioWhisperTool
    
    tool = AudioWhisperTool()
    assert tool is not None

