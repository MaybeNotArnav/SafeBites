from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime

class Session:
    session_id:str
    user_id:str
    restaurant_id:str
    active:bool = True
    created_at:datetime = datetime.utcnow()
    