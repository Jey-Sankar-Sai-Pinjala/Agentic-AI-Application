from typing import Dict, Optional
from app.schemas.models import ExtractedContent
from datetime import datetime, timedelta
import threading


class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
        self.lock = threading.Lock()
        self.session_timeout = timedelta(hours=1)
    
    def store_extracted_content(self, session_id: str, extracted_content: ExtractedContent):
        with self.lock:
            if session_id not in self.sessions:
                self.sessions[session_id] = {}
            self.sessions[session_id]['extracted_content'] = extracted_content
            self.sessions[session_id]['last_activity'] = datetime.now()
    
    def get_extracted_content(self, session_id: str) -> Optional[ExtractedContent]:
        with self.lock:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                last_activity = session.get('last_activity', datetime.now())
                if datetime.now() - last_activity > self.session_timeout:
                    del self.sessions[session_id]
                    return None
                session['last_activity'] = datetime.now()
                return session.get('extracted_content')
            return None
    
    def update_activity(self, session_id: str):
        with self.lock:
            if session_id in self.sessions:
                self.sessions[session_id]['last_activity'] = datetime.now()
    
    def clear_session(self, session_id: str):
        with self.lock:
            if session_id in self.sessions:
                del self.sessions[session_id]


session_manager = SessionManager()

