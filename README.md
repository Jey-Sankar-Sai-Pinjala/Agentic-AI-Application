# Agentic AI Application

Academic-grade Agentic AI Application with Planner and Executor agents, built with FastAPI and Google Gemini.

## Demo

Watch the demo video to see the application in action:
- [Demo Video](agentic%20ai.mp4) - Full demonstration of all features

> **Note:** The demo video file (`agentic ai.mp4`) is included in the repository. Click the link above or download it directly to view.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                           │
│                 (HTML/CSS/JS Frontend)                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND                           │
│                      (main.py)                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
  ┌──────────────────┐      ┌──────────────────┐
  │  PLANNER AGENT   │      │  EXECUTOR AGENT  │
  │ (Intent Analysis)│─────▶│(Tool Execution)  │
  └────────┬─────────┘      └────────┬─────────┘
           │                         │
           │                         │
           ▼                         ▼
  ┌──────────────────┐      ┌──────────────────┐
  │   GEMINI TEXT    │      │      TOOLS       │
  │(Intent Detection)│      │ ┌──────────────┐  │
  └──────────────────┘      │ │ Gemini Text  │  │
                            │ │ Gemini Vision│  │
                            │ │ PDF Parser   │  │
                            │ │ OCR          │  │
                            │ │ Whisper      │  │
                            │ │ YouTube      │  │
                            │ │ Summarizer   │  │
                            │ │ Sentiment    │  │
                            │ │ Code Explainer│ │
                            │ └──────────────┘  │
                            └──────────────────┘
```

## Features

### Input Support
- ✅ Raw text
- ✅ Images (JPG/PNG) with OCR
- ✅ PDF documents (text-based and scanned)
- ✅ Audio files (MP3/WAV/M4A)
- ✅ YouTube URLs (auto-transcript fetching)

### Core Capabilities
1. **Content Extraction**
   - Image → Gemini Vision OCR → pytesseract fallback
   - PDF → pdfplumber → OCR fallback
   - Audio → Whisper transcription
   - YouTube → transcript API

2. **Intent Understanding**
   - Intent detection using Gemini
   - Ambiguity detection
   - Automatic clarification questions

3. **Task Execution**
   - Summarization (1-line, 3 bullets, 5 sentences)
   - Sentiment analysis (label, confidence, justification)
   - Code explanation (functionality, bugs, time complexity)
   - Conversational Q&A

4. **Follow-up Question Rule**
   - If intent is ambiguous → Ask clarification
   - Executor does NOT run until clarity is received

## Tech Stack

### Backend
- Python 3.10+
- FastAPI
- Pydantic
- Google Gemini API (`google-generativeai`)
- Whisper / faster-whisper
- pdfplumber
- pytesseract
- youtube-transcript-api

### Frontend
- HTML + CSS + JavaScript
- Chat-style UI

## Installation

### Prerequisites
- Python 3.10 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Tesseract OCR (for OCR fallback)
  - Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
  - macOS: `brew install tesseract`
  - Linux: `sudo apt-get install tesseract-ocr`

### Setup

1. **Clone or navigate to the project directory**
   ```bash
   cd "ai chatbot"
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API key**

   **Option 1: Create a `.env` file (Recommended)**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Then edit .env and add your API key
   GOOGLE_API_KEY=your-api-key-here
   ```

   **Option 2: Set environment variable**
   ```bash
   # Windows PowerShell
   $env:GOOGLE_API_KEY="your-api-key-here"
   
   # Windows CMD
   set GOOGLE_API_KEY=your-api-key-here
   
   # macOS/Linux
   export GOOGLE_API_KEY="your-api-key-here"
   ```

5. **Configure Tesseract (if using OCR fallback)**
   - Windows: Add Tesseract to PATH or set `TESSDATA_PREFIX` environment variable
   - The OCR tool will auto-detect if Tesseract is available

## Running the Application

1. **Start the FastAPI server**
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Open the UI**
   - Navigate to `http://localhost:8000` in your browser
   - Or open `ui/index.html` directly (note: file uploads won't work without the backend)

## Usage Examples

### 1. Text Summarization
```
Input: "Summarize this text: [your text here]"
Or upload a text file and ask: "Summarize this"
```

### 2. Image OCR
```
Upload an image (JPG/PNG) with text
Ask: "Extract text from this image"
```

### 3. PDF Text Extraction
```
Upload a PDF file
Ask: "Extract text from this PDF"
```

### 4. Audio Transcription + Summary
```
Upload an audio file (MP3/WAV/M4A)
Ask: "Transcribe and summarize this audio"
```

### 5. YouTube Transcript
```
Paste a YouTube URL
Ask: "Get the transcript" or "Summarize this video"
```

### 6. Sentiment Analysis
```
Input: "Analyze the sentiment of: [your text]"
```

### 7. Code Explanation
```
Paste code or upload a code file
Ask: "Explain this code" or "What does this code do?"
```

### 8. General Q&A
```
Ask any question: "What is machine learning?"
```

## Project Structure

```
.
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── planner.py          # Planner Agent (intent detection)
│   │   └── executor.py          # Executor Agent (tool execution)
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── gemini_text.py       # Gemini text API
│   │   ├── gemini_vision.py     # Gemini vision API
│   │   ├── pdf_parser.py        # PDF text extraction
│   │   ├── ocr.py               # OCR fallback
│   │   ├── audio_whisper.py     # Audio transcription
│   │   ├── youtube.py           # YouTube transcripts
│   │   ├── summarizer.py        # Text summarization
│   │   ├── sentiment.py         # Sentiment analysis
│   │   └── code_explainer.py    # Code explanation
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── models.py             # Pydantic models
│   ├── config.py                 # Configuration
│   ├── main.py                   # FastAPI application
│   └── session_manager.py        # Session management
├── ui/
│   └── index.html                # Frontend UI
├── tests/
│   ├── test_planner.py
│   ├── test_executor.py
│   └── test_tools.py
├── samples/
│   ├── sample_code.py
│   ├── sample_text.txt
│   └── README.md
├── main.py                        # Entry point
├── requirements.txt
├── .env.example
├── .gitignore
├── agentic ai.mp4                 # Demo video
└── README.md
```

## API Endpoints

### POST `/chat`
Main chat endpoint for processing requests.

**Request Body:**
```json
{
  "message": "Summarize this text",
  "file_path": "/path/to/file.pdf",
  "file_type": "pdf",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "extracted_content": {...},
  "intent_detection": {...},
  "planner_decision": {...},
  "execution_result": {...},
  "timestamp": "...",
  "session_id": "..."
}
```

### POST `/upload`
Upload a file (image/PDF/audio).

**Response:**
```json
{
  "file_path": "/tmp/filename.pdf",
  "file_type": "pdf",
  "filename": "filename.pdf"
}
```

### GET `/health`
Health check endpoint.

## Testing

Run tests with pytest:
```bash
pytest tests/
```

## Explainability

Every request returns:
- ✅ Detected intent
- ✅ Planned steps
- ✅ Tools selected
- ✅ Any fallback used
- ✅ Execution results

## Error Handling

- Robust error handling at all levels
- Graceful fallbacks (Gemini Vision → OCR, pdfplumber → OCR)
- Clear error messages to users
- Logging for debugging

## Constraints & Design Decisions

1. **Text-only final outputs**: All results are text-based
2. **No guessing intent**: If ambiguous, ask for clarification
3. **Modular design**: Clean separation of concerns
4. **Academic clarity**: Code is well-commented and structured

## Troubleshooting

### "GOOGLE_API_KEY not found"
- Set the `GOOGLE_API_KEY` environment variable
- Or create a `.env` file with your API key

### OCR not working
- Install Tesseract OCR
- Add to PATH or configure `pytesseract.pytesseract.tesseract_cmd`

### Whisper errors
- Install `faster-whisper` or `openai-whisper`
- For faster-whisper, ensure you have the required dependencies

### PDF parsing issues
- Ensure `pdfplumber` is installed
- For scanned PDFs, OCR fallback will be used automatically

