from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel


class ChatState(BaseModel):
    user_id:str
    session_id:str
    restaurant_id:str
    query:str
    intents:Optional[List[Dict[str,Any]]] = None
    context:Optional[Dict[str,Any]] = None
    query_parts: Optional[Dict[str,Any]] = None
    menu_results: Optional[Dict[str,List[Dict[str, Any]]]] = None
    info_results: Optional[Dict[str,Dict[str, Any]]] = None
    data : Dict[str,Any] = {}
    response : str = ""
    status : str = "pending"
    timestamp : str = datetime.utcnow().isoformat()