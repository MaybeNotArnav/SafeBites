"""
Defines the Session model used to represent a user session in the SafeBites backend.

The Session model encapsulates all relevant metadata about a user's interaction with
the system within a restaurant context, including session ID, associated user and
restaurant IDs, activity status, and creation timestamp.

This model is primarily used for session management, tracking active interactions,
and linking chat or menu queries to a specific user session.
"""
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime

class Session:
    """
    Represents a user session within the system, typically used to track
    ongoing interactions between a user and a restaurant context.

    Attributes:
        session_id (str): Unique identifier for the session.
        user_id (str): Identifier for the user associated with the session.
        restaurant_id (str): Identifier for the restaurant context of the session.
        active (bool): Indicates whether the session is currently active.
        created_at (datetime): Timestamp marking when the session was created.
    """
    session_id:str
    user_id:str
    restaurant_id:str
    active:bool = True
    created_at:datetime = datetime.utcnow()