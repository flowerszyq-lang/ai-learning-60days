from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Optional

class ConversationMemory:
    def __init__(self, max_history: int = 10):
        self.sessions: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        self.max_history = max_history

    def add_message(self, session_id: str, role: str, content: str):
        self.sessions[session_id].append({"role": role, "content": content})
        if len(self.sessions[session_id]) > self.max_history:
            self.sessions[session_id] = self.sessions[session_id][-self.max_history:]

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        return self.sessions.get(session_id, [])

    def clear(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

# 全局单例
memory_store = ConversationMemory()