from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Conversation
from ..schemas import ConversationCreate, ConversationDetail, ConversationOut, MessageOut

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

def owned(db, conversation_id, session_id):
    item = db.get(Conversation, conversation_id)
    if not item or item.session_id != session_id: raise HTTPException(404, "Conversation not found")
    return item

@router.get("", response_model=list[ConversationOut])
def list_conversations(session_id: str = Query(min_length=12, max_length=80), search: str = "", db: Session = Depends(get_db)):
    query = select(Conversation).where(Conversation.session_id == session_id)
    if search.strip(): query = query.where(Conversation.title.ilike(f"%{search.strip()}%"))
    return db.scalars(query.order_by(Conversation.updated_at.desc())).all()

@router.post("", response_model=ConversationOut, status_code=201)
def create_conversation(payload: ConversationCreate, db: Session = Depends(get_db)):
    item = Conversation(session_id=payload.session_id, title=payload.title.strip())
    db.add(item); db.commit(); db.refresh(item); return item

@router.get("/{conversation_id}", response_model=ConversationDetail)
def get_conversation(conversation_id: str, session_id: str = Query(min_length=12, max_length=80), db: Session = Depends(get_db)):
    return owned(db, conversation_id, session_id)

@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
def messages(conversation_id: str, session_id: str = Query(min_length=12, max_length=80), db: Session = Depends(get_db)):
    return owned(db, conversation_id, session_id).messages

@router.delete("/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: str, session_id: str = Query(min_length=12, max_length=80), db: Session = Depends(get_db)):
    db.delete(owned(db, conversation_id, session_id)); db.commit()
