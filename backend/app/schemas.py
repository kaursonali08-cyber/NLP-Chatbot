from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    conversation_id: str | None = Field(default=None, max_length=36)
    message: str = Field(min_length=1, max_length=2000)
    session_id: str = Field(min_length=12, max_length=80)
    @field_validator("message")
    @classmethod
    def clean_message(cls, value):
        value = value.strip()
        if not value: raise ValueError("Message cannot be blank")
        return value


class ChatResponse(BaseModel):
    conversation_id: str; response: str; intent: str; confidence: float
    response_source: str; timestamp: datetime
    memory_conflict: dict | None = None


class ConversationCreate(BaseModel):
    session_id: str = Field(min_length=12, max_length=80)
    title: str = Field(default="New conversation", min_length=1, max_length=120)


class MessageOut(BaseModel):
    id: str; role: str; content: str; timestamp: datetime
    detected_intent: str | None = None; confidence: float | None = None; response_source: str | None = None
    model_config = {"from_attributes": True}


class ConversationOut(BaseModel):
    id: str; title: str; created_at: datetime; updated_at: datetime
    model_config = {"from_attributes": True}


class ConversationDetail(ConversationOut):
    messages: list[MessageOut]


class AnalysisOut(BaseModel):
    original_text: str; tokens: list[str]; lemmas: list[str]; content_tokens: list[str]
    language: str; intent: str; confidence: float; entities: list[dict]; semantic_similarity: float


class MemoryFactOut(BaseModel):
    id: str; conversation_id: str; original_statement: str; subject: str; predicate: str | None = None
    object_text: str | None = None; temporal_context: str; language: str; polarity: str; status: str
    extraction_confidence: float; created_at: datetime
    model_config = {"from_attributes": True}


class MemoryUpdate(BaseModel):
    original_statement: str | None = Field(default=None, min_length=1, max_length=2000)
    status: str | None = Field(default=None, pattern="^(active|superseded|disputed|deleted)$")


class MemoryCreate(BaseModel):
    session_id: str = Field(min_length=12, max_length=80)
    conversation_id: str = Field(min_length=1, max_length=36)
    statement: str = Field(min_length=1, max_length=2000)


class ContradictionOut(BaseModel):
    id: str; earlier_fact_id: str; current_fact_id: str; semantic_similarity: float | None = None
    entailment_score: float | None = None; neutral_score: float | None = None; contradiction_score: float | None = None
    temporal_compatible: bool; decision: str; model_name: str | None = None; status: str; created_at: datetime
    model_config = {"from_attributes": True}


class ContradictionResolve(BaseModel):
    session_id: str = Field(min_length=12, max_length=80)
    action: str = Field(pattern="^(update_memory|keep_both|earlier_incorrect|dismiss)$")
    note: str | None = Field(default=None, max_length=500)
