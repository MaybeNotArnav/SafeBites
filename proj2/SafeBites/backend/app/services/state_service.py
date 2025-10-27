from datetime import datetime
from bson import ObjectId

from ..flow.state import ChatState
from ..db import db
import uuid

chat_states = db["chat_states"]
sessions = db["sessions"]

def get_or_create_session(user_id:str, restaurant_id:str):
    existing_session = sessions.find_one({"user_id": user_id, "restaurant_id": restaurant_id,"active":True})

    if existing_session:
        return sessions["session_id"]
    

    session_id = f"sess_{uuid.uuid4().hex[:10]}"
    sessions.insert_one({
        "session_id": session_id,
        "user_id": user_id,
        "restaurant_id": restaurant_id,
        "active": True,
        "created_at": datetime.utcnow()
    })
    return session_id


def save_chat_state(state:ChatState):
    chat_states.insert_one(state.dict())

def get_all_chat_states(session_id:str):
    docs = list(chat_states.find({"session_id":session_id}).sort("timestamp",1))
    return docs

def rebuild_context(session_id:str,last_n:int=5):
    chat_states = get_all_chat_states(session_id)
    context = []
    for cs in chat_states[-last_n:]:
        state = cs["state"]
        context.append({
            "query": state["query"],
            "intents": state.get("intents", []),
            "menu_results": state.get("menu_results", {}),
            "info_results": state.get("info_results", {})
        })
    return context
