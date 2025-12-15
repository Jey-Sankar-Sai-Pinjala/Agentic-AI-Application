from typing import Dict, Any, Optional, List
import time
from app.schemas.models import ExecutionResult, ToolUsage, ExtractedContent
from app.tools.gemini_text import GeminiTextTool
from app.tools.gemini_vision import GeminiVisionTool
from app.tools.pdf_parser import PDFParserTool
from app.tools.ocr import OCRTool
from app.tools.audio_whisper import AudioWhisperTool
from app.tools.youtube import YouTubeTool
from app.tools.summarizer import SummarizerTool
from app.tools.sentiment import SentimentTool
from app.tools.code_explainer import CodeExplainerTool


class ExecutorAgent:
    def __init__(self):
        self.gemini_text = GeminiTextTool()
        self.gemini_vision = GeminiVisionTool()
        self.pdf_parser = PDFParserTool()
        self.ocr = OCRTool()
        self.audio_whisper = AudioWhisperTool()
        self.youtube = YouTubeTool()
        self.summarizer = SummarizerTool(self.gemini_text)
        self.sentiment = SentimentTool(self.gemini_text)
        self.code_explainer = CodeExplainerTool(self.gemini_text)
    
    def execute(
        self,
        intent: str,
        extracted_content: Optional[ExtractedContent],
        user_message: str,
        tools_to_use: List[str]
    ) -> ExecutionResult:
        tools_used = []
        output = ""
        
        try:
            content_text = extracted_content.content if extracted_content else user_message
            
            # Combine user prompt with extracted content for files
            if extracted_content and extracted_content.source_type in ["audio", "pdf", "image", "youtube"] and user_message.strip():
                if extracted_content.source_type == "audio":
                    source_label = "Transcribed audio content"
                    context_note = "The following text was transcribed from an audio file:"
                elif extracted_content.source_type == "pdf":
                    source_label = "Extracted PDF content"
                    if "[PDF processed using Python packages" in content_text:
                        context_note = "A PDF document was uploaded and processed using Python packages (pdfplumber). However, no text could be extracted from the PDF. The PDF may be scanned/image-based, corrupted, or password-protected."
                    else:
                        context_note = "The following text was extracted from a PDF document using Python packages (pdfplumber for text-based PDFs, with OCR fallback for scanned PDFs). This text represents the content of the PDF:"
                elif extracted_content.source_type == "youtube":
                    source_label = "YouTube video transcript"
                    transcript_language = extracted_content.metadata.get("language", "unknown")
                    if transcript_language and transcript_language != "auto" and transcript_language != "unknown":
                        context_note = f"The following text is the transcript extracted from a YouTube video using youtube-transcript-api. The transcript is in {transcript_language} language. This text represents what was said in the video. Please process this transcript and fulfill the user's request (summarize, answer questions, etc.) regardless of the language:"
                    else:
                        context_note = "The following text is the transcript extracted from a YouTube video using youtube-transcript-api. This text represents what was said in the video. Please process this transcript and fulfill the user's request (summarize, answer questions, etc.):"
                else:  # image
                    source_label = "Image analysis and content"
                    if "Image Description:" in content_text:
                        context_note = "An image was uploaded and analyzed using Gemini Vision API. The following is a detailed description of the image content:"
                    elif "[Image processed but no text was detected" in content_text:
                        context_note = "An image was uploaded and processed. OCR (Optical Character Recognition) did not detect any readable text in the image. The image may contain only visual elements, graphics, or the text may not be clearly readable."
                    else:
                        context_note = "The following text was extracted from an image using OCR (Optical Character Recognition). This text represents what was visible in the image:"
                combined_prompt = f"{user_message}\n\n{context_note}\n{source_label}:\n{content_text}"
                content_text = combined_prompt
            
            # Execute based on intent
            if intent == "extract_text":
                output = extracted_content.content if extracted_content else user_message
                if extracted_content:
                    output += f"\n\n[Confidence: {extracted_content.confidence:.2f}]"
            
            elif intent == "summarize":
                text_to_summarize = content_text
                result = self.summarizer.summarize(text_to_summarize)
                if result.get("success"):
                    output = result["summary"]
                else:
                    output = f"Error: {result.get('error', 'Unknown error')}"
                tools_used.append(ToolUsage(
                    tool_name="summarizer",
                    tool_type="summarizer",
                    success=result.get("success", False),
                    execution_time=None
                ))
            
            elif intent == "sentiment_analysis":
                text_to_analyze = content_text
                result = self.sentiment.analyze_sentiment(text_to_analyze)
                if result.get("success"):
                    output = f"""SENTIMENT: {result['sentiment'].upper()}
CONFIDENCE: {result['confidence']:.2f}
JUSTIFICATION: {result['justification']}"""
                else:
                    output = f"Error: {result.get('error', 'Unknown error')}"
                tools_used.append(ToolUsage(
                    tool_name="sentiment",
                    tool_type="sentiment",
                    success=result.get("success", False),
                    execution_time=None
                ))
            
            elif intent == "code_explanation":
                result = self.code_explainer.explain_code(content_text)
                if result.get("success"):
                    output = result["explanation"]
                else:
                    output = f"Error: {result.get('error', 'Unknown error')}"
                tools_used.append(ToolUsage(
                    tool_name="code_explainer",
                    tool_type="code_explainer",
                    success=result.get("success", False),
                    execution_time=None
                ))
            
            elif intent == "transcription":
                output = extracted_content.content if extracted_content else content_text
                if extracted_content and extracted_content.metadata.get("duration"):
                    output += f"\n\n[Duration: {extracted_content.metadata['duration']:.2f} seconds]"
            
            elif intent == "qa":
                if extracted_content and extracted_content.source_type in ["audio", "pdf", "image", "youtube"]:
                    if extracted_content.source_type == "audio":
                        source_label = "Transcribed audio content"
                        context_note = "The following text was transcribed from an audio file:"
                    elif extracted_content.source_type == "pdf":
                        source_label = "Extracted PDF content"
                        if "[PDF processed using Python packages" in extracted_content.content:
                            context_note = "A PDF document was uploaded and processed using Python packages (pdfplumber). However, no text could be extracted from the PDF. The PDF may be scanned/image-based, corrupted, or password-protected."
                        else:
                            context_note = "The following text was extracted from a PDF document using Python packages (pdfplumber for text-based PDFs, with OCR fallback for scanned PDFs). This text represents the content of the PDF:"
                    elif extracted_content.source_type == "youtube":
                        source_label = "YouTube video transcript"
                        transcript_language = extracted_content.metadata.get("language", "unknown")
                        if transcript_language and transcript_language != "auto" and transcript_language != "unknown":
                            context_note = f"The following text is the transcript extracted from a YouTube video using youtube-transcript-api. The transcript is in {transcript_language} language. This text represents what was said in the video. Please process this transcript and fulfill the user's request (summarize, answer questions, etc.) regardless of the language:"
                        else:
                            context_note = "The following text is the transcript extracted from a YouTube video using youtube-transcript-api. This text represents what was said in the video. Please process this transcript and fulfill the user's request (summarize, answer questions, etc.):"
                    else:  # image
                        source_label = "Image analysis and content"
                        if "Image Description:" in extracted_content.content:
                            context_note = "An image was uploaded and analyzed using Gemini Vision API. The following is a detailed description of the image content:"
                        elif "[Image processed but no text was detected" in extracted_content.content:
                            context_note = "An image was uploaded and processed. OCR (Optical Character Recognition) did not detect any readable text in the image. The image may contain only visual elements, graphics, or the text may not be clearly readable."
                        else:
                            context_note = "The following text was extracted from an image using OCR (Optical Character Recognition). This text represents what was visible in the image:"
                    prompt_for_gemini = f"{user_message}\n\n{context_note}\n{source_label}:\n{extracted_content.content}"
                else:
                    prompt_for_gemini = user_message if user_message.strip() else content_text
                
                start_time = time.time()
                result = self.gemini_text.generate(prompt_for_gemini)
                exec_time = time.time() - start_time
                
                if result.get("text"):
                    output = result["text"]
                else:
                    output = f"Error: {result.get('error', 'Unknown error')}"
                
                tools_used.append(ToolUsage(
                    tool_name="gemini_text",
                    tool_type="gemini_text",
                    success=bool(result.get("text")),
                    execution_time=exec_time
                ))
            
            else:
                output = f"Unknown intent: {intent}. Cannot execute."
            
            return ExecutionResult(
                success=True,
                output=output,
                error=None,
                tools_used=tools_used
            )
        
        except Exception as e:
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                tools_used=tools_used
            )
    
    def extract_content_from_file(
        self,
        file_path: str,
        file_type: str
    ) -> ExtractedContent:
        tools_used = []
        
        try:
            if file_type == "image":
                start_time = time.time()
                
                vision_result = self.gemini_vision.analyze_image(
                    file_path, 
                    query="Describe this image in detail, including all visible text, objects, colors, layout, and any other relevant details."
                )
                
                exec_time = time.time() - start_time
                
                if vision_result.get("success") and vision_result.get("text"):
                    image_description = vision_result.get("text", "").strip()
                    
                    ocr_result = self.ocr.extract_text_from_image(file_path)
                    ocr_text = ocr_result.get("text", "").strip() if ocr_result.get("success") else ""
                    
                    if ocr_text:
                        combined_content = f"Image Description:\n{image_description}\n\nExtracted Text (OCR):\n{ocr_text}"
                    else:
                        combined_content = f"Image Description:\n{image_description}"
                    
                    return ExtractedContent(
                        source_type="image",
                        content=combined_content,
                        confidence=0.9,
                        metadata={
                            "method": "gemini_vision",
                            "ocr_used": bool(ocr_text),
                            "execution_time": exec_time,
                            **vision_result.get("metadata", {})
                        }
                    )
                else:
                    ocr_result = self.ocr.extract_text_from_image(file_path)
                    extracted_text = ocr_result.get("text", "").strip()
                    
                    if not extracted_text:
                        extracted_text = "[Image processed but no text was detected. The image may contain only visual elements without readable text.]"
                    
                    return ExtractedContent(
                        source_type="image",
                        content=extracted_text,
                        confidence=ocr_result.get("confidence", 0.0),
                        metadata={
                            "method": "pytesseract_fallback",
                            "execution_time": exec_time,
                            "text_found": bool(extracted_text),
                            **ocr_result.get("metadata", {})
                        }
                    )
            
            elif file_type == "pdf":
                start_time = time.time()
                result = self.pdf_parser.extract_text(file_path)
                exec_time = time.time() - start_time
                
                extracted_text = result.get("text", "").strip() if result.get("text") else ""
                
                if not extracted_text:
                    extracted_text = "[PDF processed using Python packages (pdfplumber) but no text was extracted. The PDF may be scanned/image-based, corrupted, or password-protected.]"
                
                return ExtractedContent(
                    source_type="pdf",
                    content=extracted_text,
                    confidence=result.get("confidence", 0.0),
                    metadata={
                        "execution_time": exec_time,
                        "fallback_used": result.get("fallback_used", False),
                        "text_found": bool(result.get("text", "").strip()),
                        "method": result.get("metadata", {}).get("method", "pdfplumber"),
                        **result.get("metadata", {})
                    }
                )
            
            elif file_type == "audio":
                start_time = time.time()
                result = self.audio_whisper.transcribe(file_path)
                exec_time = time.time() - start_time
                
                return ExtractedContent(
                    source_type="audio",
                    content=result.get("text", ""),
                    confidence=result.get("confidence", 0.0),
                    metadata={
                        "duration": result.get("duration", 0.0),
                        "execution_time": exec_time,
                        **result.get("metadata", {})
                    }
                )
            
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        
        except Exception as e:
            return ExtractedContent(
                source_type=file_type,
                content="",
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    def extract_content_from_youtube(self, url: str) -> ExtractedContent:
        try:
            start_time = time.time()
            result = self.youtube.fetch_transcript(url)
            exec_time = time.time() - start_time
            
            if not result.get("success"):
                error_msg = result.get("error", "Unknown error")
                return ExtractedContent(
                    source_type="youtube",
                    content=f"[YouTube transcript extraction failed: {error_msg}]",
                    confidence=0.0,
                    metadata={
                        "execution_time": exec_time,
                        "error": error_msg,
                        **result.get("metadata", {})
                    }
                )
            
            extracted_text = result.get("text", "").strip()
            if not extracted_text:
                return ExtractedContent(
                    source_type="youtube",
                    content="[YouTube transcript extraction returned empty text. The video may not have captions available.]",
                    confidence=0.0,
                    metadata={
                        "execution_time": exec_time,
                        **result.get("metadata", {})
                    }
                )
            
            return ExtractedContent(
                source_type="youtube",
                content=extracted_text,
                confidence=result.get("confidence", 0.0),
                metadata={
                    "duration": result.get("duration", 0.0),
                    "execution_time": exec_time,
                    **result.get("metadata", {})
                }
            )
        except Exception as e:
            return ExtractedContent(
                source_type="youtube",
                content=f"[Error extracting YouTube transcript: {str(e)}]",
                confidence=0.0,
                metadata={"error": str(e)}
            )
