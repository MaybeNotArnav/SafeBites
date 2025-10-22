import numpy as np
from typing import List, Dict, Any, Optional
<<<<<<< HEAD
from pydantic import BaseModel, ConfigDict
=======
from pydantic import BaseModel
>>>>>>> docs/project-documentations

class QueryIntent(BaseModel):
    positive : List[str]
    negative : List[str]

class DishHit(BaseModel):
    dish : Dict[str, Any]
    score : float
    embedding : Optional[np.ndarray] = None
<<<<<<< HEAD
    centroid_similarity : Optional[float] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
=======
    centroid_similarity : Optional[float] = None
>>>>>>> docs/project-documentations
