from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import ChatRequest, ChatResponse
from ..services.chatbot import respond

router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    try: return await respond(db, payload.session_id, payload.message, payload.conversation_id)
    except LookupError as exc: raise HTTPException(status_code=404, detail=str(exc))
