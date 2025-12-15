from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional
import os
import tempfile
import shutil
from pathlib import Path
import re

from app.schemas.models import ChatRequest, ChatResponse, ExtractedContent
from app.agents.planner import PlannerAgent
from app.agents.executor import ExecutorAgent
from app.tools.youtube import YouTubeTool
from app.session_manager import session_manager

app = FastAPI(
    title="Agentic AI Application",
    description="Academic-grade Agentic AI Application with Planner and Executor agents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

planner_agent = PlannerAgent()
executor_agent = ExecutorAgent()
youtube_tool = YouTubeTool()


def detect_youtube_url(text: str) -> Optional[str]:
    if "youtube.com" in text.lower() or "youtu.be" in text.lower():
        patterns = [
            r'https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'https?://(?:www\.)?youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                full_url_match = re.search(r'https?://[^\s]+', text)
                if full_url_match:
                    return full_url_match.group(0)
                video_id = match.group(1)
                return f"https://www.youtube.com/watch?v={video_id}"
    return None


@app.get("/", response_class=HTMLResponse)
async def root():
    ui_path = Path("ui/index.html")
    if ui_path.exists():
        with open(ui_path, "r", encoding="utf-8") as f:
            return f.read()
    return """
    <html>
        <head><title>Agentic AI Application</title></head>
        <body>
            <h1>Agentic AI Application</h1>
            <p>API is running. Use /chat endpoint or serve UI from ui/index.html</p>
        </body>
    </html>
    """


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        extracted_content = None
        session_id = request.session_id or "default"
        
        # Extract content if file is provided
        if request.file_path:
            file_type = request.file_type
            if not file_type:
                ext = Path(request.file_path).suffix.lower()
                if ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]:
                    file_type = "image"
                elif ext == ".pdf":
                    file_type = "pdf"
                elif ext in [".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac", ".wma"]:
                    file_type = "audio"
                else:
                    raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
            
            extracted_content = executor_agent.extract_content_from_file(
                request.file_path,
                file_type
            )
            
            if extracted_content:
                session_manager.store_extracted_content(session_id, extracted_content)
        else:
            # Check for stored content from previous messages
            user_message_lower = request.message.lower().strip()
            is_simple_greeting = user_message_lower in ["hi", "hello", "hey", "hi there", "hello there", "hey there", "hii", "hiii"]
            
            stored_content = session_manager.get_extracted_content(session_id)
            if stored_content and not is_simple_greeting:
                extracted_content = stored_content
            else:
                extracted_content = None
                session_manager.update_activity(session_id)
        
        # Check for YouTube URL
        youtube_url = detect_youtube_url(request.message)
        if youtube_url:
            try:
                extracted_content = executor_agent.extract_content_from_youtube(youtube_url)
                if extracted_content:
                    session_manager.store_extracted_content(session_id, extracted_content)
            except Exception as e:
                extracted_content = ExtractedContent(
                    source_type="youtube",
                    content=f"[Error processing YouTube URL: {str(e)}]",
                    confidence=0.0,
                    metadata={"error": str(e)}
                )
                session_manager.store_extracted_content(session_id, extracted_content)
        
        # Planner Agent analyzes intent
        extracted_text_for_planner = None
        if extracted_content:
            if extracted_content.content and not extracted_content.content.startswith("["):
                extracted_text_for_planner = extracted_content.content
            elif extracted_content.content:
                extracted_text_for_planner = extracted_content.content[:200] if len(extracted_content.content) > 200 else extracted_content.content
        
        analysis = planner_agent.analyze(
            request.message,
            extracted_text_for_planner
        )
        
        intent_detection = analysis["intent_detection"]
        planner_decision = analysis["planner_decision"]
        
        # Execute if planner approves
        execution_result = None
        if planner_decision.should_proceed:
            execution_result = executor_agent.execute(
                intent=intent_detection.intent,
                extracted_content=extracted_content,
                user_message=request.message,
                tools_to_use=planner_decision.tools_to_use
            )
        
        response = ChatResponse(
            extracted_content=extracted_content,
            intent_detection=intent_detection,
            planner_decision=planner_decision,
            execution_result=execution_result,
            session_id=session_id
        )
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_type = None
        ext = Path(file.filename).suffix.lower()
        if ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]:
            file_type = "image"
        elif ext == ".pdf":
            file_type = "pdf"
        elif ext in [".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac", ".wma"]:
            file_type = "audio"
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {ext}. Supported: images (.jpg, .png, .gif), PDFs (.pdf), audio (.mp3, .wav, .m4a, .ogg, .flac)"
            )
        
        temp_dir = tempfile.gettempdir()
        safe_filename = "".join(c for c in file.filename if c.isalnum() or c in "._-") or "uploaded_file"
        temp_path = os.path.join(temp_dir, safe_filename)
        
        counter = 1
        base_path = temp_path
        while os.path.exists(temp_path):
            name, ext = os.path.splitext(base_path)
            temp_path = f"{name}_{counter}{ext}"
            counter += 1
        
        try:
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as write_error:
            raise HTTPException(
                status_code=500, 
                detail=f"Error saving file: {str(write_error)}"
            )
        
        return {
            "file_path": temp_path,
            "file_type": file_type,
            "filename": file.filename
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error uploading file: {str(e)}"
        )


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Agentic AI Application"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
