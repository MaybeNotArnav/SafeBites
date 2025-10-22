from typing import Dict, List
from .state import ChatState

class StateStore:
    def __init__(self):
        self.sessions : Dict[str, List[ChatState]] = {}

    def get(self, session_id:str):
        return self.sessions.get(session_id)

    def save(self, state):
        self.sessions.setdefault(state.session_id, []).append(state)

state_store = StateStore()