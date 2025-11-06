"""
Defines Pydantic models used to represent user query intents and search results
for dishes in the SafeBites backend.

Models:

- QueryIntent: Represents positive and negative preferences extracted from a user's query.
- DishHit: Represents a retrieved dish with associated similarity scores and optional embedding metadata.

These models are used in the recommendation and retrieval pipeline to standardize
the format of inputs and outputs for vector search, filtering, and scoring.
"""
import numpy as np
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict

class QueryIntent(BaseModel):
    """
    Represents the intent extracted from a user's query, 
    distinguishing between positive and negative preferences.

    Attributes:
        positive (List[str]): A list of keywords, ingredients, or dish attributes 
            the user explicitly wants (e.g., "spicy", "vegan").
        negative (List[str]): A list of keywords, ingredients, or dish attributes 
            the user wants to avoid (e.g., "nuts", "dairy").
    """
    positive : List[str]
    negative : List[str]

class DishHit(BaseModel):
    """
    Represents a single dish retrieved from a search or recommendation system,
    along with its similarity score and optional embedding metadata.

    Attributes:
        dish (Dict[str, Any]): The dish data, typically a structured document 
            from a database or search index.
        score (float): The similarity or relevance score of the dish 
            relative to the query.
        embedding (Optional[np.ndarray]): The numerical vector representation 
            of the dish (if applicable, used in vector search or clustering).
        centroid_similarity (Optional[float]): The similarity between this dish’s 
            embedding and the centroid of a relevant cluster (if applicable).
    """
    dish : Dict[str, Any]
    score : float
    embedding : Optional[np.ndarray] = None
    centroid_similarity : Optional[float] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
