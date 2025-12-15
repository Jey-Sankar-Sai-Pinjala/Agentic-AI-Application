from typing import Dict, Any, Optional
import time


class AudioWhisperTool:
    def __init__(self, use_faster_whisper: bool = True):
        self.use_faster_whisper = use_faster_whisper
        self._model = None
    
    def _load_model(self):
        if self._model is None:
            if self.use_faster_whisper:
                try:
                    from faster_whisper import WhisperModel
                    self._model = WhisperModel("base", device="cpu", compute_type="int8")
                except ImportError:
                    import whisper
                    self._model = whisper.load_model("base")
            else:
                import whisper
                self._model = whisper.load_model("base")
        return self._model
    
    def transcribe(self, audio_path: str) -> Dict[str, Any]:
        try:
            start_time = time.time()
            model = self._load_model()
            
            if self.use_faster_whisper and hasattr(model, 'transcribe'):
                segments, info = model.transcribe(audio_path, beam_size=5)
                text_parts = []
                duration = 0.0
                
                for segment in segments:
                    text_parts.append(segment.text)
                    duration = max(duration, segment.end)
                
                transcript = " ".join(text_parts)
                confidence = 0.9
            else:
                result = model.transcribe(audio_path)
                transcript = result["text"]
                duration = result.get("segments", [{}])[-1].get("end", 0.0) if result.get("segments") else 0.0
                confidence = 0.9
            
            execution_time = time.time() - start_time
            
            return {
                "text": transcript.strip(),
                "duration": duration,
                "confidence": confidence,
                "metadata": {
                    "model": "faster-whisper" if self.use_faster_whisper else "openai-whisper",
                    "execution_time": execution_time,
                    "audio_path": audio_path
                },
                "success": True
            }
        except Exception as e:
            return {
                "text": None,
                "duration": 0.0,
                "confidence": 0.0,
                "error": str(e),
                "success": False,
                "metadata": {}
            }
