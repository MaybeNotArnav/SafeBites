from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DishData(BaseModel):
<<<<<<< HEAD
    dish_id: str
=======
>>>>>>> docs/project-documentations
    dish_name : str = Field(default="N/A")
    description : Optional[str] = None
    price : Optional[Any] = None
    ingredients : List[str] = None
    serving_size: Optional[str] = None
    availibility : Optional[str] = None
    allergens : List[str] = None
    nutrition_facts : Dict[str, Any] = {}

class DishInfoResponse(BaseModel):
    dish_name : Optional[str] = None
    requested_info : Optional[str] = None
<<<<<<< HEAD
    source_data : Optional[List[Any]] = None
=======
    source_data : Optional[str] = None
    message : Optional[str] = None
>>>>>>> docs/project-documentations

class IntentResponse(BaseModel):
    type : str

class GeneralKnowledgeResponse(BaseModel):
    answer : str

class DishInfoResult(BaseModel):
    info_results: Dict[str, DishInfoResponse]