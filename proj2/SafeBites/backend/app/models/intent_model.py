from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class IntentQuery(BaseModel):
    type:str
    query:str

class IntentExtractionResult(BaseModel):
    intents : List[IntentQuery]