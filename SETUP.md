# Quick Setup Guide

## Step-by-Step Setup

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Google Gemini API Key
```bash
# Windows PowerShell
$env:GOOGLE_API_KEY="your-api-key-here"

# Windows CMD
set GOOGLE_API_KEY=your-api-key-here

# macOS/Linux
export GOOGLE_API_KEY="your-api-key-here"
```

### 3. (Optional) Install Tesseract OCR
- **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki) and add to PATH
- **macOS**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

### 4. Run the Application
```bash
python main.py
```

### 5. Open Browser
Navigate to: `http://localhost:8000`

## Testing the Application

### Test Case 1: Text Summarization
1. Type: "Summarize this: [paste some text]"
2. Or upload `samples/sample_text.txt` and ask: "Summarize this"

### Test Case 2: Code Explanation
1. Upload `samples/sample_code.py` or paste code
2. Ask: "Explain this code"

### Test Case 3: Image OCR
1. Upload an image with text (JPG/PNG)
2. Ask: "Extract text from this image"

### Test Case 4: YouTube Transcript
1. Paste a YouTube URL
2. Ask: "Get the transcript"

### Test Case 5: Sentiment Analysis
1. Type: "Analyze sentiment: I love this product!"
2. Check the sentiment label and confidence

## Troubleshooting

### API Key Issues
- Ensure `GOOGLE_API_KEY` is set correctly
- Check that the API key is valid and has quota

### Import Errors
- Ensure you're in the project root directory
- Activate virtual environment if using one
- Run: `pip install -r requirements.txt`

### OCR Not Working
- Install Tesseract OCR
- For Windows, ensure it's in PATH or set `TESSDATA_PREFIX`

### Port Already in Use
- Change port in `main.py`: `uvicorn.run(app, host="0.0.0.0", port=8001)`

