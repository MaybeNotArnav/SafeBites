"""
Defines Pydantic models for representing user intent extraction results
in the SafeBites backend.

Models:

- IntentQuery: Represents a single intent extracted from a user’s query.
- IntentExtractionResult: Aggregates multiple extracted intents from a single user input.

These models are used throughout the conversation pipeline to standardize
how user intents are stored, processed, and passed to downstream services.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class IntentQuery(BaseModel):
    """
    Represents a single extracted intent from a user's query.

    Attributes:
        type (str): The category or type of the intent (e.g., "dish_info", "restaurant_search", "general_knowledge").
        query (str): The actual text of the user’s intent or question.
    """
    type:str
    query:str

class IntentExtractionResult(BaseModel):
    """
    Represents the result of an intent extraction process,
    containing one or more identified intents.

    Attributes:
        intents (List[IntentQuery]): A list of extracted intents from the user's input.
    """
    intents : List[IntentQuery]