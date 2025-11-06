import numpy as np
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict

class QueryIntent(BaseModel):
    positive : List[str]
    negative : List[str]

class DishHit(BaseModel):
    dish : Dict[str, Any]
    score : float
    embedding : Optional[np.ndarray] = None
    centroid_similarity : Optional[float] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
