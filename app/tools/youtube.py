from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from typing import Dict, Any, Optional
import re


class YouTubeTool:
    def __init__(self):
        pass
    
    def extract_video_id(self, url: str) -> Optional[str]:
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def fetch_transcript(self, url_or_id: str) -> Dict[str, Any]:
        try:
            video_id = self.extract_video_id(url_or_id) if "youtube" in url_or_id.lower() or "youtu.be" in url_or_id.lower() else url_or_id
            
            if not video_id:
                return {
                    "text": None,
                    "error": "Invalid YouTube URL or video ID",
                    "success": False,
                    "metadata": {}
                }
            
            try:
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
                text_parts = [entry['text'] for entry in transcript_list]
                transcript = " ".join(text_parts)
                duration = transcript_list[-1]['start'] + transcript_list[-1]['duration'] if transcript_list else 0.0
                
                return {
                    "text": transcript,
                    "duration": duration,
                    "confidence": 1.0,
                    "metadata": {
                        "video_id": video_id,
                        "entries_count": len(transcript_list),
                        "method": "youtube_transcript_api",
                        "language": "auto"
                    },
                    "success": True
                }
            except TranscriptsDisabled:
                return {
                    "text": None,
                    "error": "Transcripts are disabled for this video",
                    "success": False,
                    "metadata": {"video_id": video_id}
                }
            except NoTranscriptFound:
                try:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                    
                    try:
                        transcript = transcript_list.find_transcript(['en', 'en-US', 'en-GB'])
                        transcript_data = transcript.fetch()
                        language_used = transcript.language
                    except:
                        available_transcripts = list(transcript_list)
                        if available_transcripts:
                            transcript = available_transcripts[0]
                            transcript_data = transcript.fetch()
                            language_used = transcript.language
                        else:
                            raise Exception("No transcripts available")
                    
                    text_parts = [entry['text'] for entry in transcript_data]
                    transcript_text = " ".join(text_parts)
                    duration = transcript_data[-1]['start'] + transcript_data[-1]['duration'] if transcript_data else 0.0
                    
                    return {
                        "text": transcript_text,
                        "duration": duration,
                        "confidence": 1.0,
                        "metadata": {
                            "video_id": video_id,
                            "entries_count": len(transcript_data),
                            "method": "youtube_transcript_api",
                            "language": language_used
                        },
                        "success": True
                    }
                except Exception as fallback_error:
                    return {
                        "text": None,
                        "error": f"No transcript found for this video. Error: {str(fallback_error)}",
                        "success": False,
                        "metadata": {"video_id": video_id}
                    }
        except Exception as e:
            return {
                "text": None,
                "error": str(e),
                "success": False,
                "metadata": {}
            }
