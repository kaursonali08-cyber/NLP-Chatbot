import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .database import Base, engine
from .routes import chat, conversations, nlp

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
settings = get_settings()
app = FastAPI(title="ConversaAI API", version="1.0.0", description="Local NLP-powered conversational chatbot API")
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_origin], allow_credentials=False, allow_methods=["GET", "POST", "DELETE"], allow_headers=["Content-Type"])
app.include_router(chat.router); app.include_router(conversations.router); app.include_router(nlp.router)

@app.on_event("startup")
def startup(): Base.metadata.create_all(bind=engine)

@app.get("/api/health", tags=["health"])
async def health():
    return {"status": "ok", "ollama_model": settings.ollama_model, "ollama_endpoint": settings.ollama_base_url}
