from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..config import get_settings
from ..models import Conversation, Message
from .intent_classifier import classify
from .response_generator import generate_ollama, fallback_response
from .semantic_similarity import similarity_to_training
from .nlp_processor import detect_language


async def respond(db: Session, session_id: str, text: str, conversation_id: str | None):
    settings = get_settings()
    if conversation_id:
        conversation = db.get(Conversation, conversation_id)
        if not conversation or conversation.session_id != session_id: raise LookupError("Conversation not found")
    else:
        conversation = Conversation(session_id=session_id, title=text[:60])
        db.add(conversation); db.flush()
    language = detect_language(text)
    intent, confidence = classify(text)
    # The compact intent training set is English-only, so do not present an
    # English intent prediction as a fact for a different language.
    if language not in {"en", "unknown"}:
        intent, confidence = "unknown", 0.0
    similarity = similarity_to_training(text)
    db.add(Message(conversation_id=conversation.id, role="user", content=text, detected_intent=intent, confidence=confidence))
    db.flush()
    history = [{"role": m.role, "content": m.content} for m in conversation.messages[-settings.context_message_limit:] if m.role in {"user", "assistant"}]
    llm = await generate_ollama(text, history, settings.ollama_base_url, settings.ollama_model, settings.ai_response_timeout)
    response, source = (llm, "local_llm") if llm else fallback_response(intent, confidence, similarity, settings.intent_confidence_threshold, language)
    now = datetime.now(timezone.utc)
    db.add(Message(conversation_id=conversation.id, role="assistant", content=response, detected_intent=intent, confidence=confidence, response_source=source, timestamp=now))
    conversation.updated_at = now
    db.commit()
    return {"conversation_id": conversation.id, "response": response, "intent": intent, "confidence": confidence, "response_source": source, "timestamp": now}
