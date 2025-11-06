"""
Provides an in-memory state management system for chat sessions in SafeBites.

This module defines the `StateStore` class, which acts as a lightweight storage
for tracking the conversation history of multiple chat sessions. Each session
is identified by a unique session ID and maintains a sequence of `ChatState`
objects representing the flow of a conversation (e.g., context resolution,
intent extraction, query handling, response generation).

It is designed to facilitate rapid retrieval, saving, and management of
session states during user interactions.

Key Components:
- StateStore: Core class that stores and manages chat session states.
- state_store: Singleton instance of StateStore for global access across modules.
"""
from typing import Dict, List
from .state import ChatState

class StateStore:
    """
    A lightweight in-memory storage system for managing chat session states.

    This class maintains conversation histories for multiple sessions,
    allowing each user or chat session to have an isolated state flow.
    It stores sequences of `ChatState` objects that represent each step
    in a conversation pipeline (such as context resolution, intent extraction,
    or response synthesis).

    Attributes:
        sessions (Dict[str, List[ChatState]]): 
            A dictionary mapping session IDs to their corresponding list of chat states.
    """
    def __init__(self):
        """Initializes an empty state store for all chat sessions."""
        self.sessions : Dict[str, List[ChatState]] = {}

    def get(self, session_id:str):
        """
        Retrieve all stored states for a given session.

        Args:
            session_id (str): The unique identifier of the chat session.

        Returns:
            List[ChatState] | None: A list of `ChatState` objects for the
            given session ID, or `None` if no session exists.

        Example:
            >>> state_store.get("session_123")
            [ChatState(...), ChatState(...)]
        """
        return self.sessions.get(session_id)

    def save(self, state):
        """
        Save the current chat state to its corresponding session.

        If the session ID does not exist, it is automatically created.
        This allows the conversation to be tracked over time as multiple
        states are appended to the session’s history.

        Args:
            state (ChatState): The current chat state object to store.

        Example:
            >>> state = ChatState(session_id="session_123", user_message="Hi")
            >>> state_store.save(state)
            >>> len(state_store.get("session_123"))
            1
        """
        self.sessions.setdefault(state.session_id, []).append(state)

state_store = StateStore()