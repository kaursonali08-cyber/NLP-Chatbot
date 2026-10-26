from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


def utcnow(): return datetime.now(timezone.utc)


class Conversation(Base):
    __tablename__ = "conversations"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title: Mapped[str] = mapped_column(String(120), default="New conversation")
    session_id: Mapped[str] = mapped_column(String(80), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, index=True)
    messages: Mapped[list["Message"]] = relationship(back_populates="conversation", cascade="all, delete-orphan", order_by="Message.timestamp")


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"), index=True)
    role: Mapped[str] = mapped_column(String(16))
    content: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    detected_intent: Mapped[str | None] = mapped_column(String(64), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    response_source: Mapped[str | None] = mapped_column(String(32), nullable=True)
    conversation: Mapped[Conversation] = relationship(back_populates="messages")


Index("ix_messages_conversation_time", Message.conversation_id, Message.timestamp)


class MemoryFact(Base):
    __tablename__ = "memory_facts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    session_id: Mapped[str] = mapped_column(String(80), index=True)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"), index=True)
    source_message_id: Mapped[str | None] = mapped_column(ForeignKey("messages.id"), nullable=True, index=True)
    original_statement: Mapped[str] = mapped_column(Text)
    subject: Mapped[str] = mapped_column(String(96), default="user")
    predicate: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    object_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    temporal_context: Mapped[str] = mapped_column(String(32), default="unspecified")
    language: Mapped[str] = mapped_column(String(16), default="unknown")
    polarity: Mapped[str] = mapped_column(String(16), default="affirmed")
    status: Mapped[str] = mapped_column(String(16), default="active", index=True)
    extraction_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    embedding_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class ContradictionEvent(Base):
    __tablename__ = "contradiction_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    session_id: Mapped[str] = mapped_column(String(80), index=True)
    earlier_fact_id: Mapped[str] = mapped_column(ForeignKey("memory_facts.id"), index=True)
    current_fact_id: Mapped[str] = mapped_column(ForeignKey("memory_facts.id"), index=True)
    semantic_similarity: Mapped[float | None] = mapped_column(Float, nullable=True)
    entailment_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    neutral_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    contradiction_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    temporal_compatible: Mapped[bool] = mapped_column(default=True)
    decision: Mapped[str] = mapped_column(String(32), default="insufficient_information")
    model_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class MemoryCorrection(Base):
    __tablename__ = "memory_corrections"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    session_id: Mapped[str] = mapped_column(String(80), index=True)
    fact_id: Mapped[str] = mapped_column(ForeignKey("memory_facts.id"), index=True)
    event_id: Mapped[str | None] = mapped_column(ForeignKey("contradiction_events.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(32))
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


Index("ix_memory_facts_session_status", MemoryFact.session_id, MemoryFact.status)
Index("ix_contradictions_session_status", ContradictionEvent.session_id, ContradictionEvent.status)
