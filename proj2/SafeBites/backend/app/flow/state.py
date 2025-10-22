from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel
from ..models.dish_info_model import DishInfoResult, DishInfoResponse, DishData
from ..models.intent_model import IntentExtractionResult
from ..models.restaurant_model import MenuResultResponse

class ChatState(BaseModel):
    user_id:str
    session_id:str
    restaurant_id:str
    query:str
    # intents:Optional[List[Dict[str,Any]]] = None
    intents:Optional[IntentExtractionResult] = None
<<<<<<< HEAD
    context:Optional[List[Dict[str,Any]]] = None
=======
    context:Optional[Dict[str,Any]] = None
>>>>>>> docs/project-documentations
    query_parts: Optional[Dict[str,Any]] = None
    # menu_results: Optional[Dict[str,List[Dict[str, Any]]]] = None
    menu_results: Optional[MenuResultResponse] = None
    # info_results: Optional[Dict[str,Dict[str, Any]]] = None
<<<<<<< HEAD
    info_results: Optional[DishInfoResult] = None
=======
    info_results: Optional[Dict[str,DishInfoResponse]] = None
>>>>>>> docs/project-documentations
    data : Dict[str,Any] = {}
    response : str = ""
    status : str = "pending"
    timestamp : str = datetime.utcnow().isoformat()